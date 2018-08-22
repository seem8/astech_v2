#!/usr/bin/env python3
'''
Astech is a web frontend for the MegaMek game.
Consider this an Alpha stage code.
author: Łukasz Posadowski
mail: mail [at] lukaszposadowski.pl
'''

import tarfile, urllib.request, shutil  # MegaMek download and install/uninstall
import os, os.path                      # ------ // --------
import subprocess                       # running and stopping MegaMek
import datainterface as dit      # sqlite commands


###########################################
#        Custom Errors for tests          #
###########################################

class WrongMegamekUrl(Exception): pass
class WrongMegamekFileName(Exception): pass
class NotaTarFile(Exception): pass
class WrongMegamekVersion(Exception): pass
class MegamekNotInstalled(Exception): pass

###########################################
#         MegaMek instance class          #
###########################################

class MegaTech:
  def __init__(self, idx):
    '''Init function for MegaTech,
    params: idx:int
    returns -> MegaTech instance'''

    # mega = (idx, name, version, port, is_on, game_password):tuple
    mega = dit.megamek_list(idx)

    self.idx = mega[0]
    self.name = mega[1]
    self.version = mega[2]
    self.port = mega[3]

    # MegaMek server is turned off by default
    if mega[4] == 't':
      self.ison = True
    elif mega[4] == 'f':
      self.ison = False

    # MegaMek server is without a password by default
    self.game_password = mega[5]

    # subprocess of running MegaMek instance
    self.process = False

    # some variables, usefull when MegaMek is installed
    self.maindir = f'./mek/installed/{self.idx}/megamek-{self.version}/'
    self.mapdir = f'{self.maindir}data/boards/astech/'
    self.unitdir = f'{self.maindir}data/mechfiles/astech/'
    self.savedir = f'{self.maindir}savegames/'
    self.logfile = f'{self.maindir}logs/megameklog.txt'


  def setup(self,
            new_name=False,
            new_version=False,
            new_game_password=False):
    '''Setter for MegaMek data and db file
    params: new_name:str, new_version:str, new_game_password:str.
    returns: newsets{'name': bool, 'ver': bool, 'paswd': bool}:dict'''

    # checking what was changed and what were the problems
    newsets = {
               'name': False,
               'ver': False,
               'paswd': False,
               'problems': [],
               }

    if new_name and new_name != self.name:
      try:
        dit.megamek_changename(self.idx, new_name)
        self.name = new_name
        newsets['name'] = True
      except dit.NameInUse:
        newsets['problems'].append('NameInUse')
      except dit.NameNotAlpha:
        newsets['problems'].append('NameNotAlpha')
      except dit.NameTooLarge:
        newsets['problems'].append('NameTooLarge')

    if new_version and new_version != self.verion:
      dit.megamek_changever(self.idx, new_version)
      self.version = new_version
      # updating path to MegaMek installation 
      self.maindir = f'./mek/installed/{self.idx}/megamek-{self.version}/'
      self.mapdir = f'{self.maindir}data/boards/astech/'
      self.unitdir = f'{self.maindir}data/mechfiles/astech/'
      self.savedir = f'{self.maindir}savegames/'
      self.logfile = f'{self.maindir}logs/megameklog.txt'
      newsets['ver'] = True

    if new_game_password and new_game_password != self.game_password:
      try:
        dit.megamek_changepass(self.idx, new_game_password)
        self.game_password = new_game_password
        newsets['paswd'] = True
      except dit.PasswordNotAlpha:
        newsets['problems'].append('PasswordNotAlpha')
      except dit.PasswordTooSimple:
        newsets['problems'].append('PasswordTooSimple')
      except dit.PasswordTooLarge:
        newsets['problems'].append('PasswordTooLarge')

    return newsets


  def is_installed(self):
    '''Checks if MegaMek is installed.
    return: True or False'''
    if os.path.isdir(self.maindir):
      return True
    return False


  def startserver(self):
    '''Starts a server described in MegaTech instance.
    returns True, or MegamekNotInstalled.'''

    if not self.is_installed():
      raise MegamekNotInstalled

    # we don't want server duplicates
    if self.ison:
      return False

    javabin = '/usr/java/default/bin/java'

    # command to run MegaMek headless server
    command = f'{javabin} -jar MegaMek.jar -dedicated -port {str(self.port)}'

    # add password if present
    if self.game_password != '':
      command += f' -p {self.game_password}'

    # we're running server now
    self.process = subprocess.Popen(command.split(), cwd=self.maindir)
    self.ison = True
    dit.megamek_switchon(self.idx, 't')
    return True


  def checkserver(self):
    '''check if MegaMek is running
    return True, or False'''
    try:
      # none means the process is running
      if self.process.poll() is None:
        dit.megamek_switchon(self.idx, 't')
        self.ison = True
        return True
      # any other result means it's not
      dit.megamek_switchon(self.idx, 'f')
      self.ison = False
      return False
    except AttributeError:
      # in case if the process wansn't initialised yet
      dit.megamek_switchon(self.idx, 'f')
      self.ison = False
      return False


  def stopserver(self):
    '''stops MegaMek server,
    return True, or False'''
    if self.ison == True:
      self.process.kill()
      dit.megamek_switchon(self.idx, 'f')
      self.ison = False
      return True
    return False


  def loglines(self):
    '''returns: reverserd last 81 lines of logfile'''
    if not os.path.isfile(self.logfile):
      open(self.logfile,'w').close()
    with open(self.logfile,'r') as myfile:
      mylines = myfile.readlines()
      # we need just 81 last lines
      lastlog = mylines[len(mylines)-81 : len(mylines)]
      lastlog.reverse()
      # sometimes the word in file is too long to fit inside template div,
      # so I'm inserting '\n' all over the lines;
      # in tpl it is interpreted by SPACE character (I don't know why),
      # which is capable to break like if necessary;
      # TODO it adds werid looking spaces into a log file view
      for line in range(len(lastlog)):
        l = list(lastlog[line])
        try:
          for idx in (50, 101, 152, 203, 254, 305, 356, 407, 458, 509):
            l.insert(idx, '\n')
        except IndexError:
          pass
        lastlog[line] = ''.join(l)
      return lastlog


###########################################
#  Download MegaMek archive from GitHub   #
###########################################

def download_megamek(version,
                     redownload=False,
                     directory='./mek/archives/',
                     ):
  '''Downloads provided MegaMek version into provided directory.
  params:
  version:str,
  directory:str (with unix "/" dir style),
  redownload:bool,

  returns -> True, or WrongMegamekUrl, or WrongMegamekFileName, or NotaTarFile'''

  # url of MegaMek archive on GitHub project page
  url = 'http://github.com/MegaMek/megamek/releases/download/'

  # some versions are stored in unusual location
  if version == '0.43.10-RC4':
    url += 'v0.43.10/megamek-v0.43.10-RC4.tar.gz'
  elif version == '0.42.2':
    url += 'v42.2/megamek-0.42.2.tar.gz'
  else:
    url += f'v{version}/megamek-{version}.tar.gz'

  # directory and file namd for saved megamek-[version].tar.gz file
  file_name = f'{directory}/megamek-{version}.tar.gz'

  # nothing do to in that case
  if not redownload and os.path.isfile(file_name):
    return True

  if redownload:
    if os.path.isfile(file_name):
      os.remove(file_name)

  try:
    # downloading megamek-[version].tar.gz
    with urllib.request.urlopen(url) as response, open(file_name, 'wb') as mek_archive:
      shutil.copyfileobj(response, mek_archive)
  # I'm pretty sure that my hosting and GitHub are both online,
  # so any HTTPError is due to wrong url
  except urllib.error.HTTPError:
    raise WrongMegamekUrl
  # in case that downloaded file name doesn't exist
  except FileNotFoundError:
    raise WrongMegamekFileName

  # returns something for easier testing
  return True


###########################################
#    Install MegaMek from an archive      #
###########################################

def install_megamek(idx, version,
                    archivedir='./mek/archives/',
                    installdir='./mek/installed/',
                    reinstall=False,
                    ):
  '''Untar MegaMek into [installdir],
  makes various subdirectories in it.
  params:
  idx:int,
  version:str,
  archivedir:str (with unix "/" dir style),
  installdir:str (with unix "/" dir style).

  returns True, os NotaTarFile, or FileNotFoundError'''

  # here is our "installer" archive and install path
  mm_archive = f'{archivedir}megamek-{version}.tar.gz'
  instpath = f'{installdir}{idx}/'
  megapath = f'{instpath}/megamek-{version}/'

  # in case MegaMek is installed and we don't
  # reinstall, there is nothing to do
  if not reinstall and os.path.isdir(instpath):
    return True

  # we're checking if provided filemane is an archive,
  # to verify that is was downloaded correctly
  if not tarfile.is_tarfile(mm_archive):
    raise NotaTarFile

  # if we are reinstalling, removing now
  if reinstall:
    if os.path.isdir(f'{installdir}{idx}'):
      shutil.rmtree(f'{installdir}{idx}')

  # installing MegaMek
  with tarfile.open(mm_archive, 'r:gz') as megatar:
    megatar.extractall(instpath)
  #tar = tarfile.open(mm_archive, 'r:gz')
  #tar.extractall(instpath)

  # making files and subdirectories needed for astech
  if not os.path.isdir(f'{megapath}savegames'):
    os.mkdir(f'{megapath}savegames')

  if not os.path.isdir(f'{megapath}data/boards/astech'):
    os.mkdir(f'{megapath}data/boards/astech')

  if not os.path.isdir(f'{megapath}data/mechfiles/astech'):
    os.mkdir(f'{megapath}data/mechfiles/astech')

  open(f'{megapath}logs/megameklog.txt', 'w').close()

  # returns something for easier testing
  return True


###########################################
#   Uninstall MegaMek from install dir    #
###########################################

def uninstall_megamek(version, directory='./mek/installed/'):
  '''Uninstall specified version of MegaMek.
  params: version:str,
  directory:str (with unix "/" style dir),

  returns: True, or WrongMegamekVersion.'''

  # here is our install path
  instpath = f'{directory}megamek-{version}/'

  # incorrect install path
  if not os.path.isdir(instpath):
    raise WrongMegamekVersion

  # correct install path
  shutil.rmtree(instpath)
  return True

