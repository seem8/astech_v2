import pytest

from .. import astech

mega1 = astech.MegaTech(idx=1)
mega2 = astech.MegaTech(idx=2)
mega3 = astech.MegaTech(idx=3)


def test_mega1_init():
  assert mega1.name == 'firstmek', 'MegaTech instance should have name(str).'
  assert mega1.version == '', 'Megatech instance should have version(str).'
  assert mega1.port == 2500, 'Megatech instance should have port(int).'

  assert mega1.ison is False, 'Should be False as MegaMek is off by default.'
  assert mega1.game_password == '', 'Should be empty string.'

  assert mega1.maindir == './mek/installed/1/megamek-/',\
    'Should provide path to MegaMek installation.'

  assert mega1.logfile == './mek/installed/1/megamek-/logs/megameklog.txt',\
    'Should provide path to megameklog.txt.'

  assert mega1.mapdir == './mek/installed/1/megamek-/data/boards/astech/',\
    'Should provide path for MegaMek board files.'

  assert mega1.unitdir == './mek/installed/1/megamek-/data/mechfiles/astech/',\
    'Should provide path for MegaMek unit files.'

  assert mega1.savedir == './mek/installed/1/megamek-/savegames/',\
    'Should provide path for MegaMek saved game files.'

# --------------------------------------

def test_mega1_setup_name():
  assert mega1.setup(new_name='campaign')['name'] is True, 'Should return True after changing attribute.'


def test_mega2_setup_name_with_existing_name():
  assert mega2.setup(new_name='campaign')['name'] is False, 'Should return False after name validation.'

# --------------------------------------

def test_mega1_setup_ver():
  assert mega1.setup(new_version='0.44.0')['ver'] is True, 'Should return True after changing attribute.'

# --------------------------------------

def test_mega3_setup_password():
  assert mega3.setup(new_game_password='urbiedurbie')['paswd'] is True, 'Should return True after chaging attribute'


def test_mega3_setup_password_with_non_latin_password():
  assert mega3.setup(new_game_password='urbie1')['paswd'] is False, 'Should return False after password validation.'


def test_mega3_setup_password_with_weak_password():
  assert mega3.setup(new_game_password='foo')['paswd'] is False, 'Should return False after password validation.'

