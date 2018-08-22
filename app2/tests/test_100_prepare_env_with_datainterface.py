import pytest

from .. datainterface import UserNotAlpha, PasswordNotAlpha, \
                             PasswordTooSimple, PasswordTooLarge, \
                             OldPasswordNotMatch, NewPasswordNotMatch, \
                             BadUserName, NameInUse, NameTooLarge, NameNotAlpha, \
                             create_user, change_password, read_hashpass, \
                             check_hashpass, user_is_activated, \
                             megamek_add, megamek_remove, megamek_changename, \
                             megamek_changever, megamek_changepass, \
                             megamek_switchon, megamek_list, \
                             cookie_create, cookie_read


###########################################
#            user and password            #
###########################################

def test_create_user_with_good_data():
  assert create_user('first', 'somepassword') == True, 'Should return True after sql inserts.'


def test_create_user_with_nonlatin_password():
  with pytest.raises(PasswordNotAlpha, message='Should return PasswordNotAlpha for non-latin password.'):
    create_user('second', 'some123456')


def test_create_user_with_nonlatin_user():
  with pytest.raises(UserNotAlpha, message='Should return UserNotAlpha for non-latin user.'):
    create_user('third3', 'somepassword')


def test_create_user_with_nonlatin_user_and_password():
  with pytest.raises(UserNotAlpha, message='Should return UserNotAlpha, because it checks user first.'):
    create_user('fourth4', 'some123456')


def test_create_user_with_weak_password():
  with pytest.raises(PasswordTooSimple, message='Should return PasswordTooSimple with len(password)<6.'):
    create_user('sixth', 'short')


def test_user_is_activated_with_non_activated_user():
  assert user_is_activated('first') is False, 'Should return False with non-activated user.'


def test_user_is_activated_with_user_that_not_exists():
  with pytest.raises(BadUserName, message='Should raise BadUserName for user that not exists.'):
    user_is_activated('foooo')

# --------------------------------------

def test_readhash_of_user_first():
  assert read_hashpass('first') == 'a1d292f556aa661b720847487960860f17086a0bd11a4320368e9447ff7139de089aa88b6159420814f10194f1aa55a3379fb80ea26ba6397ba75cec811b241a', 'Should be sha512 of "somepassword"'


def test_readhash_of_user_that_not_exist():
  with pytest.raises(BadUserName, message='Should raise BadUserName, because "wronguser" does not exist.'):
    read_hashpass('wronguser')


def test_check_hashpass_with_good_data():
  assert check_hashpass('first', 'somepassword') is True, 'Should return True for good password.'


def test_check_hashpass_for_user_that_not_exist():
  with pytest.raises(BadUserName, message='Should raise BadUserName if user does not exist.'):
    assert check_hashpass('wronguser', 'bar')


def test_check_password_with_wrong_password():
  assert check_hashpass('first', 'wrong') is False, 'Should return False for wrong password.'

# --------------------------------------

def test_changepassword_of_user_that_not_exist():
  with pytest.raises(BadUserName, message='Should raise BadUserName, because "wronguser" does not exist.'):
    change_password('wronguser', 'somepassword', 'somenewpassword', 'somenewpassword')


def test_changepassword_with_bad_old_password():
  with pytest.raises(OldPasswordNotMatch, message='Should raise OldPasswordNotMatch with sha512 of current password is different from sha512 of old password argument.'):
    change_password('first', 'badoldpassword', 'somenewpassword', 'somenewpassword')


def test_changepassword_with_different_new_passwords():
  with pytest.raises(NewPasswordNotMatch, message='Should raise NewPasswordNotMatch with different password and password confirmation arguments.'):
    change_password('first', 'somepassword', 'somenewpassword', 'somedifferentpassword')


def test_changepassword_with_non_latin_passwords():
  with pytest.raises(PasswordNotAlpha, message='Should return PasswordNotAlpha if password is not latin.'):
    change_password('first', 'old12345', 'somenew123', 'somenew123')


def test_change_password_with_weak_new_password():
  with pytest.raises(PasswordTooSimple, message='Should return PasswordTooSimple if len(new1||new2)<6'):
    change_password('first', 'somepassword', 'short', 'short')


def test_change_password_with_very_long_password():
  with pytest.raises(PasswordTooLarge, message='Should raise PasswordTooLarge if len(password)>100.'):
    change_password('first', 'somepassword', 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm', 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm')


def test_change_password_with_good_arguments():
  assert change_password('first', 'somepassword', 'somenewpassword', 'somenewpassword') == True, \
    'Should return True after sql updates.'


def test_user_is_activated_with_activated_user():
  assert user_is_activated('first') is True, 'Should return True with activated user.'


def test_readhash_of_user_first_with_somenewpassword():
  assert read_hashpass('first') == 'c86680b1fa907c90dfa86a07e7d03906861608a00ff986865ad81f9ac6896b9d55adb255cb39547b9d05a687e3ae467f00acd302f0f94a6e93ade3fafe71eb73', 'Should be sha512 of "somenewpassword"'


###########################################
#                 megamek                 #
###########################################


def test_megamek_add_initial_config():
  assert megamek_add(idx=1, name='first', version='', port=2500, is_on='f', game_password='') == True, 'Should return True after sql inserts.'
  assert megamek_add(idx=2, name='second', version='', port=2501, is_on='f', game_password='') == True, 'Should return True after sql inserts.'
  assert megamek_add(idx=3, name='third', version='', port=2502, is_on='f', game_password='') == True, 'Should return True after sql inserts.'


def test_megamek_add_with_existing_name():
  with pytest.raises(NameInUse, message='Should raise NameInUse, when name is not unique.'):
    assert megamek_add(idx=4, name='first', version='', port=2504, is_on='f', game_password='')

# --------------------------------------

def test_megamek_list():
  assert megamek_list(1) == (1, 'first', '', 2500, 'f', ''), 'Should return tuple with megamek1 config.'
  assert megamek_list(2) == (2, 'second', '', 2501, 'f', ''), 'Should return tuple with megamek2 config.'
  assert megamek_list(3) == (3, 'third', '', 2502, 'f', ''), 'Should return tuple with megamek3 config.'

# --------------------------------------

def test_megamek_remove():
  assert megamek_remove(3) is True, 'Should return True after sql delete.'
  assert megamek_add(idx=3, name='third', version='', port=2502, is_on='f', game_password='') == True, 'Should return True after sql inserts.'

# --------------------------------------

def test_megamek_changename_with_new_name():
  assert megamek_changename(1, 'firstmek') is True, 'Should return True after sql update.'


def test_megamek_changename_with_non_latin_name():
  with pytest.raises(NameNotAlpha, message='Should raise NameNotAlpha after name valisadion'):
    megamek_changename(1, 'first1mek')


def test_megamek_changename_with_existing_name():
  with pytest.raises(NameInUse, message='Should raise NameInUse if name is not inuque.'):
    megamek_changename(2, 'firstmek')


def test_megamek_changename_with_long_name():
  with pytest.raises(NameTooLarge, message='Should raise NameTooLarge if len(name)>20.'):
    megamek_changename(2, 'qwertyuiopasdfghjklzxcvbnm')

# --------------------------------------

def test_megamek_changever():
  assert megamek_changever(1, '0.44.0') == True, 'Should return True after sql update.'
  assert megamek_changever(1, '') == True, 'Should return True after sql update.'

# --------------------------------------

def test_megamek_changepass_with_good_password():
  assert megamek_changepass(1, 'urbiedurbie') == True, 'Should return True after sql update.'
  assert megamek_changepass(1, '') == True, 'Should return True after sql update.'


def test_megamek_changepass_with_nonlatin_password():
  with pytest.raises(PasswordNotAlpha, message='Should return PasswordNotAlpha for non latin password'):
    megamek_changepass(1, 'urbie12345')


def test_megamek_changepass_with_weak_password():
  with pytest.raises(PasswordTooSimple, message='Should raise PasswordTooSimple for len(game_password)<5.'):
    megamek_changepass(1, 'foo')


def test_megamek_changepass_with_long_password():
  with pytest.raises(PasswordTooLarge, message='Should raise PasswordTooLarge for len(game_password)>40.'):
    megamek_changepass(1, 'qwertyuiopasdfghjklzxcvbnmqwertyuiopasdfghjklzxcvbnm')

# --------------------------------------

def test_magemek_switchon():
  assert megamek_switchon(1, 't') == True, 'Should return True after sql update.'
  assert megamek_switchon(1, 'f') == True, 'Should return True after sql update.'


###########################################
#                 cookies                 #
###########################################


def test_cookie_create():
  assert cookie_create() == True, 'Should return True after sql inserts.'

# --------------------------------------

def test_cookie_read_alpha():
  assert 33 < len(cookie_read('alpha')) < 43, 'Should be a long string of letters and nubers.'


def test_cookie_read_beta():
  assert 33 < len(cookie_read('beta')) < 43, 'Should be a long string of letters and nubers.'

