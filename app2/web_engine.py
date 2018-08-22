#!/usr/bin/env python3
'''Megamek server administration page.
This is ALPHA quality software,
expect some bugs and glitches.
author: Łukasz Posadowski,  mail [at] lukaszposadowski.pl'''

# we have to append date to filenames 
import time

# to remove user uploaded files
import os

# import bottle
# remember to comment out ', debug'  for production
from bottle import template, response, request, get, post, error, \
                    redirect, static_file, run, route, debug

import astech
import datainterface as dit


# ----------------------------------------
# ------- COOKIE SECRETS -----------------
# ----------------------------------------

# restoring secrets from database
secret1 = dit.cookie_read('alpha')
secret2 = dit.cookie_read('beta')


# ----------------------------------------
# ------- MEGATECH INITS -----------------
# ----------------------------------------

mega1 = astech.MegaTech(idx=1)
mega2 = astech.MegaTech(idx=2)
mega3 = astech.MegaTech(idx=3)

# lauch MegaMek if neccesary 
if mega1.ison:
  mega1.startserver()
  time.sleep(1)
if mega2.ison:
  mega2.startserver()
  time.sleep(1)
if mega3.ison:
  mega3.startserver()
  time.sleep(1)


# ----------------------------------------
# ------- HELPER FUNCTIONS ---------------
# ----------------------------------------

# curTech cookie is used in nearly every
# @get, so I wrote functions for it;
# get current astech, choosen by the user
def get_curtech():
  '''Returns a number 1, or 2, or 3,
  based on cookie 'curTech'.'''
  curtech = request.get_cookie('curTech', secret=secret1)
  if not curtech or curtech not in ('1', '2', '3'):
    response.set_cookie('curtech', '1', secret=secret1)
    return 1
  return int(curtech)


def set_curtech(number):
  '''Sets cookie with choosen astech.
  Params number:int,
  returns number:int, or False'''
  if number not in (1,2,3):
    return False
  response.set_cookie('curtech', str(number), secret=secret1)
  return number


# ----------------------------------------
# ------- STATIC FILES -------------------
# ----------------------------------------

# images
@route('/img/<filename>')
def image(filename):
  return static_file(filename, root='./static/', mimetype='image/png')


# style.css file
@route('/style')
def style():
  return static_file('style.css', root='./static/')
# ----------------------------------------


# download and remove user uploaded files
@route('/files/<operation>/<filetype>/<filename>')
def downloadfile(filetype, filename):
  # check if we are logged in before download, to prevent link guessing
  username = request.get_cookie('loguser', secret=secret1)
  if username:
    # check MegaMek instance to download from
    if get_curtech() == 1:
      choosen = mega1
    elif get_curtech() == 2:
      choosen = mega2
    elif get_curtech() == 3:
      choosen = mega3

    if choosen:
      # filetype define directory with files to download
      if filetype == 'map':
        rootdir = choosen.map_dir
      elif filetype == 'savegame':
        rootdir = choosen.save_dir
      elif filetype == 'unit':
        rootdir = choosen.unit_dir

    if not rootdir:
      # er404 leads to nothing, so it will return 404 error page
      redirect('/404page')
      return False

    if operation == 'download':
      # force download
      return static_file(filename, root=rootdir, download=filename)
    elif operation == 'remove':
      # remove the file
      try:
        os.remove(rootdir + filename)
        # os.remove is displaying blank page, so we have to
        # quickly return to maps, saves, or units page
        redirect(request.get_cookie('curpage', secret=secret1))
        return True
      except FileNotFoundError:
        redirect('/404page')
        return False
    else:
      redirect('/404page')
      return False

  elif not username:
    # if we're not logged, show login page
    redirect('/login')
# ----------------------------------------


# ----------------------------------------
# ------- LOGIN PAGE ---------------------
# ----------------------------------------

# a little login template
@get('/login')
def login():
  # username variable is required for header template
  username = request.get_cookie('loguser', secret=secret1)

  if username:
    # if user is logged in, skip login page
    redirect('/')
    return True

  # cookie with information about bad password
  badpassword = request.get_cookie('badPassword', secret=secret2)

  return template('login', badpassword=badpassword, username=username)
# ----------------------------------------


# check credentials and redirect to other routes
@post('/login')
def check_login():
  # check if username and password aren't something like '/logout'
  if request.forms.get('username').isalpha() and request.forms.get('password').isalpha():
    username = request.forms.get('username')
    password = request.forms.get('password')

    # check credentials from the form
    if not dit.check_hashpass(username, password):
      # bad password
      response.set_cookie('badPassword', 'badPassword', max_age=5, secret=secret2)
      redirect('/login')
      return False
    else:
      # good password
      response.set_cookie('loguser', username, secret=secret1)
      response.delete_cookie('badPassword')

      if not dit.user_is_activated(username):
        # force password change
        response.set_cookie('userActivate', max_age=5, secret=secret2)
        redirect('/options')
        return False

      # succesfull login
      redirect('/')
      return True

  else:
    # if login and/or password are not alpha, don't parse them
    # and redirect to login (just to be safe)
    response.set_cookie('badPassword', 'nopass', max_age=5, secret=secret2)
    redirect('/login')
    return False


# ----------------------------------------
# ------- CHANGE PASSWORD ----------------
# ----------------------------------------

@get('/options')
def options_page():
  # username variable is required for header template
  username = request.get_cookie('loguser', secret=secret1)

  if username:
    # current page
    response.set_cookie('curpage', '/options', secret=secret1)

    # checks if help messages will be displayed
    veteran = request.get_cookie('veteran', secret=secret1)

    # if this is an account activation, template will show help message
    activate = request.get_cookie('userActivate', secret=secret2)

    # cookie with information about bad password
    noalpha = request.get_cookie('noAlpha', secret=secret2)
    badoldpassword = request.get_cookie('badOldPassword', secret=secret2)
    mismatchpassword = request.get_cookie('mismatchPassword', secret=secret2)
    shortnewpassword = request.get_cookie('shortNewPassword', secret=secret2)
    longnewpassword = request.get_cookie('longNewPassword', secret=secret2)

    return template('options',
                    username=username,
                    veteran=veteran,
                    activate=activate,
                    noalpha=nolpha,
                    badoldpassword=badoldpassword,
                    mismatchpassword=mismatchpassword,
                    shortnewpassword=shortnewpassword,
                    longnewpassword=longnewpassword,
                    curtech=get_curtech(),
                    )
# ----------------------------------------


@post('/options')
def change_password():
  username = request.get_cookie('loguser', secret=secret1)

  if username:
    # check if username and password aren't something like '/logout'
    if not request.forms.get('old').isalpha() \
      or not request.forms.get('new1').isalpha() \
      or not requests.forms.get('new2').isalpha():
      response.set_cookie('noAlpha', 'noAlpha', max_age=5, secret=secret2)
      redirect('/options')
      return False

    # old password, new password and confirm new password
    old = request.forms.get('old')
    new1 = request.forms.get('new1')
    new2 = request.forms.get('new2')

    try:
      # setting up new password
      dit.changepass(username, old, new1, new2)
    except dit.PasswordNotAlpha:
      response.set_cookie('noAlpha', 'noAlpha', max_age=5, secret=secret2)
      redirect('/options')
      return False
    except dit.OldPasswordNotMatch:
      response.set_cookie('badOldPassword', 'badOldPassword', max_age=5, secret=secret2)
      redirect('/options')
      return False
    except dit.PasswordTooSimple:
      response.set_cookie('shortNewPassword', 'shortNewPassword', max_age=5, secret=secret2)
      redirect('/options')
      return False
    except dit.PasswordTooLarge:
      response.set_cookie('longNewPassword', 'longNewPassword', max_age=5, secret=secret2)
      redirect('/options')
      return False
    except dit.PasswordNotMatch:
      response.set_cookie('mispatchPassword', 'mismatchPassword', max_age=5, secret=secret2)
      redirect('/options')
      return False

  elif not username:
    redirect('/login')

# ----------------------------------------

# ----------------------------------------
# ------- USER FILES PAGE ----------------
# ----------------------------------------

# files view and upload form 
@get('/files')
def list_user_files():
  username = request.get_cookie('loguser', secret=secret1)

  if username:
    # checks if help messages will be displayed
    veteran = request.get_cookie('veteran', secret=secret1)

    # current page for become_veteran and become_rookie functions
    response.set_cookie('curpage', '/files', secret=secret1)

    # current astech
    if get_curtech() == 1:
      choosen = mega1
    elif get_curtech() == 2:
      choosen = mega2
    elif get_curtech() == 3:
      choosen = mega3

    # specify directory with the files
    map_list = os.listdir(choosen.mapdir)
    unit_list = os.listdir(choosen.unitdir)
    save_list = os.listdir(choosen.savedir)

    map_list.sort()
    unit_list.sort()
    save_list.sort()

    # cookies set when uploaded file is wrong
    wrongfile = request.get_cookie('wrongfile', secret=secret2)
    bigfile = request.get_cookie('bigfile', secret=secret2)
    nofile = request.get_cookie('nofile', secret=secret2)
    longname = request.get_cookie('longname', secret=secret2)

    # render web page with template
    return template('files',
                     username=username,
                     veteran=veteran,
                     curpage=curpage,
                     choosen=choosen,
                     map_list=map_list,
                     unit_list=unit_list,
                     save_list=save_list,
                     wrongfile=wrongfile,
                     bigfile=bigfile,
                     nofile=nofile,
                     longname=longname,
                     curtech=get_curtech(),
                     )

  elif not username:
    redirect('/login')
# ----------------------------------------


# checking and uploading files
@post('/files')
def upload_file():
  username = request.get_cookie('loguser', secret=secret1)
  if username:
    # current astech
    if get_curtech() == 1:
      choosen = mega1
    elif get_curtech() == 2:
      choosen = mega2
    elif get_curtech() == 3:
      choosen = mega3

    posted_file = request.files.get('posted_file')
    try:
      name, ext = os.path.splitext(posted_file.filename)
    except AttributeError:
      # in a case when no file was uploaded;
      # page template will show error message with this cookie
      response.set_cookie('nofile', 'nofile', max_age=5, secret=secret2)
      redirect(request.get_cookie('curpage', secret=secret1))
      return False

    if len(name) > 40:
      response.set_cookie('longname', 'longname', max_age=5, secret=secret2)
      redirect(request.get_cookie('curpage', secret=secret1))
      return False

    response.delete_cookie('nofile')
    # specify correct path to save uploaded file and filesize limit
    if ext == '.board':
      file_path = choosen.mapdir
      size_limit = 1500000
    elif ext == '.mtf':
      file_path = choosen.unitdir
      size_limit = 1000000
    elif ext == 'sav.gz':
      file_path = choosen.savedir
      size_limit = 1000000
    else:
      # page template will show error message with this cookie
      response.set_cookie('wrongfile', 'wrongfile', max_age=5, secret=secret2)
      redirect(request.get_cookie('curpage', secret=secret1))
      return False

    # uploading and checking file in correct MegaMek directory
    posted_file.save(file_path, overwrite=True)
    filestats = os.stat(file_path + posted_file.filename)
    response.delete_cookie('wrongfile')

    # checking filesize and, if bigger than size limit, delete file
    if filestats.st_size > size_limit:
      # page template will show error message with this cookie
      response.set_cookie('bigfile', 'bigfile', max_age=5, secret=secret2)
      os.remove(file_path + posted_file.filename)
    else:
      response.delete_cookie('bigboard')

    # sometimes os.listdir isn't including new file right away
    time.sleep(1)
    redirect(request.get_cookie('curpage', secret=secret1))

  elif not username:
    redirect('/login')
# ----------------------------------------

# ----------------------------------------
# ----------- INDEX PAGE -----------------
# ----------------------------------------

@get('/')
def index_page():
  username = request.get_cookie('loguser', secret=secret1)

  if username:
    # checks if help messages will be displayed
    veteran = request.get_cookie('veteran', secret=secret1)

    response.set_cookie('curpage', '/', secret=secret1)

    # getting current astech and check if MegaMek
    # is still running (it crash sometimes)
    if get_curtech() == 1:
      mega1.checkserver()
      choosen = mega1
    elif get_curtech() == 2:
      mega2.checkserver()
      choosen = mega2
    elif get_curtech() == 3:
      mega3.checkserver()
      choosen = mega3

    # long list of cookies to display various
    # error and confirmation messages to the user
    name_ok = request.get_cookie('setupNameOK', secret=secret2)
    ver_ok = request.get_cookie('setupVerOK', secret=secret2)
    paswd_ok = request.get_cookie('setupPaswdOK', secret=secret2)
    name_in_use = request.get_cookie('setupNameInUse', secret=secret2)
    name_not_alpha = request.get_cookie('setup', secret=secret2)
    name_too_large = request.get_cookie('setup', secret=secret2)
    paswd_not_alpha = request.get_cookie('setupPaswdNotAlpha', secret=secret2)
    paswd_too_simple = request.get_cookie('setupPaswdTooSimple', secret=secret2)
    paswd_too_large = request.get_cookie('setupPaswdTooLarge', secret=secret2)

    return template('index',
                    username=username,
                    veteran=veteran,
                    name=choosen.name,
                    ver=choosen.version,
                    port=str(choosen.port),
                    gamepas=choosen.game_password,
                    logs=choosen.loglines(),
                    curtech=get_curtech(),

                    name_ok=name_ok,
                    ver_ok=ver_ok,
                    paswd_ok=paswd_ok,
                    name_in_use=name_in_use,
                    name_not_alpha=name_not_alpha,
                    name_too_large=name_too_large,
                    paswd_not_alpha=paswd_not_alpha,
                    paswd_too_simple=paswd_too_simple,
                    paswd_too_large=paswd_too_large,
                    )

  elif not username:
    redirect('/login')
# ----------------------------------------


@post('/')
def megamek_setup():
  username = request.get_cookie('loguser', secret=secret1)
  if username:
    # current astech
    if get_curtech() == 1:
      choosen = mega1
    elif get_curtech() == 2:
      choosen = mega2
    elif get_curtech() == 3:
      choosen = mega3

    # get name, version and password for MegaMek
    form_name = request.forms.get('name')
    form_ver = request.forms.get('ver')
    form_paswd = request.forms.get('paswd')

    # changing astech.MegaTech attributes
    new_setup = choosen.setup(new_name=form_name,
                              new_ver=form_ver,
                              new_game_password=form_paswd)

    # display error messages to the user
    if len(new_setup['problems']) > 0:
      # since not everything was OK
      response.detele_cookie('setupNameOK')
      response.detele_cookie('setupVerOK')
      response.delete_cookie('setupPaswdOK')

      # tracking individual errors
      if 'NameInUse' in new_setup['problems']:
        response.set_cookie('setupNameInUse', 'setupNameInUse', max_age=5, secret=secret2)

      if 'NameNotAlpha' in new_setup['problems']:
        response.set_cookie('setupNameNotAlpha', 'setupNameNotAlpha', max_age=5, secret=secret2)

      if 'NameTooLarge' in new_setup['problems']:
        response.set_cookie('setupNameTooLarge', 'setupNameTooLarge', max_age=5, secret=secret2)

      if 'PasswordNotAlpha' in new_setup['problems']:
        response.set_cookie('setupPasswordNotAlpha', 'setupPasswordNotAlpha', max_age=5, secret=secret2)

      if 'PasswordTooSimple' in new_setup['problems']:
        response.set_cookie('setupPasswordTooSimple', 'setupPasswordTooSimple', max_age=5, secret=secret2)

      if 'PasswordTooLarge' in new_setup['problems']:
        response.set_cookie('setupPasswordTooLarge', 'setupPasswordTooLarge', max_age=5, secret=secret2)

    else:
      # display setup confirmation messages to the user
      if new_setup['name'] is not False:
        response.set_cookie('setupNameOK', 'setupNameOK', max_age=5, secret=secret2)

      if new_setup['ver'] is not False:
        response.set_cookie('setupVerOK', 'setupVerOK', max_age=5, secret=secret2)

      if new_setup['paswd'] is not False:
        response.set_cookie('setupPaswdOK', 'setupPaswdOK', max_age=5, secret=secret2)

      # since everything was OK
      response.delete_cookie('setupNameInUse')
      response.delete_cookie('setupNameNotAlpha')
      response.delete_cookie('setupNameTooLarge')
      response.delete_cookie('setupPasswordNotAlpha')
      response.delete_cookie('setupPasswordTooSimple')
      response.delete_cookie('setupPasswordTooLarge')

    redirect('/')

  else:
    redirect('/login')


# ----------------------------------------
# Little routes that call functions.

# turn on MegaMek server via MegaTech class
@route('/launch')
def lauch_megamek():
  if request.get_cookie('loguser', secret=secret1):
    if get_curtech() == 1:
      mega1.start()
      time.sleep(1)
    elif get_curtech() == 2:
      mega2.start()
      time.sleep(1)
    elif get_curtech() == 3:
      mega3.start()
      time.sleep(1)
  redirect('/')
# ----------------------------------------


# turn off MegaMek server via MegaTech class
@route('/stop')
def stop_megamek():
  if request.get_cookie('loguser', secret=secret1):
    if get_curtech() == 1:
      mega1.stop()
      time.sleep(1)
    elif get_curtech() == 2:
      mega2.stop()
      time.sleep(1)
    elif get_curtech() == 3:
      mega3.stop()
      time.sleep(1)
  redirect('/')
# ----------------------------------------


# download and install MegaMek
@route('/install/<version>/<redownload>/<reinstall>')
def download_and_install():
  if request.get_cookie('loguser', secret=secret1):
    if get_curtech() == 1:
      dir_id = '1'
    elif get_curtech() == 2:
      dir_id = '2'
    elif get_curtech() == 3:
      dir_id = '3'
    else:
      redirect('/404page')
      return False

    if redownload == 'redownload':
      astech.download_megamek(str(version), redownload=True)
    elif redownload == 'noredownload':
      astech.download_megamek(str(version))
    else:
      redirect('/404page')
      return False

    try:
      if reinstall == 'reinstall':
        astech.install_megamek(idx=dir_id, version=str(version), reinstall=True)
      elif reinstall == 'noreinstall':
        astech.install_megamek(idx=dir_id, version=str(version))
      else:
        redirect('404page')
        return False
    except astech.NotaTarFile:
      response.set_cookie('installNotaTarFile', 'installNotaTarFile', max_age=5, secret=secret2)
      redirect('/')
      return False
# ----------------------------------------


# logout from astech
@route('/logout')
def logoff():
  response.delete_cookie('loguser')
  redirect('/login')
# ----------------------------------------


# set vetran cookie to hide tutorial messages
@route('/veteran')
def become_veteran():
  if request.get_cookie('loguser', secret=secret1):
    response.set_cookie('veteran', 'veteran', secret=secret1)
    # curpage cookie is storing current page (route)
    redirect(request.get_cookie('curpage', secret=secret1))
# ----------------------------------------


# delete veteran cookie to show tutorial messages 
@route('/green')
def become_green():
  if request.get_cookie('loguser', secret=secret1):
    response.delete_cookie('veteran')
    # curpage cookie is storing current page (route)
    redirect(request.get_cookie('curpage', secret=secret1))
# ----------------------------------------


# change current tech
@route('/switchtech/<newtech>')
def switch_tech():
  if request.get_cookie('loguser', secret=secret1):
    if newtech not in ('1', '2', '3'):
      redirect('/404page')
      return False

    set_curtech(int(number))
    redirect(request.get_cookie('curpage', secret=secret1))
# ----------------------------------------


# 404 error page
@error(404)
def route404(error):
  '''Page not found page.'''
  return template('error404')
# ----------------------------------------


# ----------------------------------------
# ----- ALL SYSTEMS... NOMINAL -----------
# ----------------------------------------
# main debug loop
# remember to add debug import from bottle
debug(True)
run(host='localhost', port=8080, reloader=True)

# main production loop
# remember to delete debug import from bottle
#run(host='0.0.0.0', port=8080)


