import pytest

import os, os.path
from ..astech import MegaTech


mega1 = MegaTech(idx=1)

def test_is_mega1_installed_with_installed_megamek():
  assert mega1.is_installed() is True, 'Should return true, because MegaMek is installed.'


def test_mega1_class_megamek_paths():
  # main dir
  assert mega1.maindir == './mek/installed/1/megamek-0.44.0/',\
    'Should provide path for MegaMek installation.'

  assert os.path.isdir(mega1.maindir),\
    'Dir mek/installed/megamek-[version]/ should exist.'

  # logs dir
  assert os.path.isfile('./mek/installed/1/megamek-0.44.0/logs/megameklog.txt'),\
    'megameklog.txt is absent by default in MegaMek, but have to be created.'

  assert os.path.isfile(mega1.logfile),\
    'Dir mek/installed/megamek-[version]/logs should exist.'

  # map dir
  assert mega1.mapdir == './mek/installed/1/megamek-0.44.0/data/boards/astech/',\
    'Should provide path for MegaMek board files.'

  assert os.path.isdir(mega1.mapdir),\
    'Dir mek/installed/megamek-[version]/data/boards/astech should exist.'

  # unit dir
  assert mega1.unitdir == './mek/installed/1/megamek-0.44.0/data/mechfiles/astech/',\
    'Should provide path for MegaMek unit files.'

  assert os.path.isdir(mega1.unitdir),\
    'Dir mek/installed/megamek-[version]/data/mechfiles/astech/ should exist.'

  # saves dir
  assert mega1.savedir == './mek/installed/1/megamek-0.44.0/savegames/',\
    'Should provide path for MegaMek saved game files.'

  assert os.path.isdir(mega1.savedir),\
    'Dir mek/installed/megamek-[version]/savegames/ should exist.'

