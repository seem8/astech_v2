#!/usr/bin/env python3
'''Glue code for a sqlite database.'''

import sqlite3
import hashlib
import random
import string

class UserNotAlpha(Exception): pass
class PasswordNotAlpha(Exception): pass
class PasswordTooSimple(Exception): pass
class PasswordTooLarge(Exception): pass
class OldPasswordNotMatch(Exception): pass
class NewPasswordNotMatch(Exception): pass
class BadUserName(Exception): pass
class NameNotAlpha(Exception): pass
class NameInUse(Exception): pass
class NameTooLarge(Exception): pass

dbfile = './config/config.db'


###########################################
#         username and password           #
###########################################

def create_user(username, password):
  '''creating user
  params: username:str, password:str,
  return: True, UserNotAlpha, or PasswordNotAlpha, or PasswordTooShort.'''

  # we have to be sure is credentials do not
  # include python code (simple and works)
  if not username.isalpha():
    raise UserNotAlpha
  if not password.isalpha():
    raise PasswordNotAlpha
  if len(password) < 6:
    raise PasswordTooSimple

  hashpass = hashlib.sha512(password.encode()).hexdigest()

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('''CREATE TABLE IF NOT EXISTS users(username TEXT(30) UNIQUE, hashpass TEXT(130), is_activated TEXT(1))''')
  c.execute('''INSERT INTO users (username, hashpass, is_activated) values (?,?,'f')''',\
            (username, hashpass,))
  conn.commit()
  c.close()
  conn.close()
  return True


def change_password(username, old, new1, new2):
  '''changes password for username,
  params: username:str, old:str, new1:str, new2:str
  return True, or BadUserName, OldPasswordNotPatch, or NewPasswordNotMatch, PasswordNotAlpha'''

  if not old.isalpha() or not new1.isalpha() or not new2.isalpha():
    raise PasswordNotAlpha
  if new1 != new2:
    raise NewPasswordNotMatch
  if len(new1) < 6 or len(new2) < 6:
    raise PasswordTooSimple
  if len(new1) > 100 or len(new2) > 100:
    raise PasswordTooLarge

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  # check current password
  old_hashpass = c.execute('''SELECT hashpass FROM users WHERE username=?''', (username,)).fetchone()

  if not old_hashpass:
    raise BadUserName

  if old_hashpass[0] != hashlib.sha512(old.encode()).hexdigest():
    c.close()
    conn.close()
    raise OldPasswordNotMatch

  newhashpass = hashlib.sha512(new1.encode()).hexdigest()

  c.execute('''UPDATE users SET hashpass=?, is_activated='t' WHERE username=?''',\
            (newhashpass, username))
  conn.commit()
  c.close()
  conn.close()
  return True


def user_is_activated(username):
  '''Checks if user changed a password, or not.
  params: username:str,
  returns True, or False, or BadUserName'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  is_activated = c.execute('''SELECT is_activated FROM users WHERE username=?''', (username,)).fetchone()
  c.close()
  conn.close()

  # if no result from the database
  if not is_activated:
    raise BadUserName

  # return True if user is activated, or False it not 
  if is_activated[0] == 'f':
    return False
  return True


def read_hashpass(username):
  '''Reads hashed password from database,
  params: username:str,
  returns hashpass:str or BadUserName.'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  myhash = c.execute('''SELECT hashpass FROM users WHERE username=?''', (username,)).fetchone()
  c.close()
  conn.close()

  # if no result from the database
  if not myhash:
    raise BadUserName

  # return hashed password
  return myhash[0]


def check_hashpass(username, password):
  '''Reads hashed password from database,
  params: username:str, password: str,
  returns True, or False, or BadUserName.'''

  if not password.isalpha():
    raise PasswordNotAlpha

  hashpass = hashlib.sha512(password.encode()).hexdigest()

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  myhash = c.execute('''SELECT hashpass FROM users WHERE username=?''', (username,)).fetchone()
  c.close()
  conn.close()

  # if no result from the database
  if not myhash:
    raise BadUserName

  if hashpass == myhash[0]:
    # password match
    return True
  elif hashpass != myhash[0]:
    # password not match
    return False


###########################################
#              MegaMek data               #
###########################################


def megamek_add(idx, name, version, port, is_on='f', game_password=''):
  '''Add new megamek server,
  params: megamek_id:int, version:str, port:int, is_on:str, game_password:str
  returns True'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  try:
    c.execute('''CREATE TABLE IF NOT EXISTS megameks(idx INTEGER UNIQUE, name TEXT(20) UNIQUE, version TEXT(20), port INTEGER, is_on TEXT(1), game_password TEXT(40))''')
    c.execute('''INSERT INTO megameks(idx, name, version, port, is_on, game_password) values (?,?,?,?,?,?)''',\
              (idx, name, version, port, is_on, game_password,))
  except sqlite3.IntegrityError:
    # the only variable that we don't have in control is name
    raise NameInUse
    c.close()
    conn.close()
    return False

  conn.commit()
  c.close()
  conn.close()
  return True


def megamek_remove(idx):
  '''Remove MegaMek from the list.
  params: idx:int.
  Return: True.'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()
  c.execute('''DELETE FROM megameks WHERE idx=?''', (idx,))
  conn.commit()
  c.close()
  conn.close()
  return True


def megamek_changename(idx, name):
  '''Changes version of MegaMek.
  params: idx:int, name:string,
  return: True, or NameNotAlpha, or NameTooLarge, or NameInUse'''

  if not name.isalpha():
    raise NameNotAlpha

  if len(name) > 20:
    raise NameTooLarge

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  try:
    c.execute('''UPDATE megameks SET name=? where idx=?''', (name, idx,))
    conn.commit()
  except sqlite3.IntegrityError:
    # name must be unique
    c.close()
    conn.close()
    raise NameInUse

  c.close()
  conn.close()
  return True


def megamek_changever(idx, version):
  '''Changes version of MegaMek.
  params: idx:int, version:string,
  return: True'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('''UPDATE megameks SET version=?, is_on='f' where idx=?''', (version, idx,))
  conn.commit()
  c.close()
  conn.close()
  return True


def megamek_changepass(idx, game_password=''):
  '''Changes version of MegaMek.
  params: idx:int, game_password:string,
  return: True'''

  if game_password != '' and not game_password.isalpha():
    raise PasswordNotAlpha

  if game_password != '' and len(game_password) < 5:
    raise PasswordTooSimple

  if len(game_password) > 40:
    raise PasswordTooLarge

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('''UPDATE megameks SET game_password=? where idx=?''',
            (game_password, idx))
  conn.commit()
  c.close()
  conn.close()
  return True


def megamek_switchon(idx, is_on):
  '''Changes version of MegaMek.
  params: idx:int, is_on:string,
  return: True'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('''UPDATE megameks SET is_on=? where idx=?''',
            (is_on, idx))
  conn.commit()
  c.close()
  conn.close()
  return True


def megamek_list(idx):
  '''Read data from megameks,
  return [(idx:int, name_str, version:str, ison:str):tuple)]:list'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  megamek = c.execute('''SELECT * FROM megameks where idx=?''', (idx,)).fetchone()
  c.close()
  conn.close()
  return megamek


###########################################
#             Cookie secrets              #
###########################################


def cookie_create():
  '''Create cookie table with random secrets.
  return: True'''

  random.seed()
  alpha = ''.join(random.choices(string.ascii_letters + string.digits, \
                                   k=34+random.randint(0,8)))
  beta = ''.join(random.choices(string.ascii_letters + string.digits, \
                                   k=34+random.randint(0,8)))

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  c.execute('''CREATE TABLE IF NOT EXISTS cookies(idx TEXT(5) UNIQUE, body TEXT(45))''')
  c.execute('''INSERT INTO cookies(idx, body) values ('alpha',?)''', (alpha,))
  c.execute('''INSERT INTO cookies(idx, body) values ('beta',?)''', (beta,))

  conn.commit()
  c.close()
  conn.close()
  return True


def cookie_read(letter):
  '''Reads cookie from database,
  return secret:str.'''

  conn = sqlite3.connect(dbfile)
  c = conn.cursor()

  secret = c.execute('''SELECT body FROM cookies ORDER BY idx''').fetchall()
  c.close()
  conn.close()
  if letter == 'alpha':
    return secret[0][0]
  elif letter == 'beta':
    return secret[1][0]

