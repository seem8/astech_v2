import pytest

import os, tarfile
import os.path
from .. astech import MegaTech, install_megamek, NotaTarFile

mega1 = MegaTech(idx=1)
mega2 = MegaTech(idx=2)

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# !! BEWARE: if you have a hard link to ~ dir inside megamek and you !!
# !! enable reinstall (like in the 5th test), you'll LOOSE ALL DATA  !!
# !! (no, I haven't tried, but I'm pretty sure)                      !!
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

# install_megamek extracts specified archive
# to the ./mek/installed/[idx]/ directory

def test_install_megamek_with_correct_filename_and_type():
  assert install_megamek(idx=1, version='0.44.0'), \
  'Should return true when filename and path are both correct.'


def test_megatech_setup_with_installed_megamek_0440():
  assert mega1.setup(new_version='0.44.0')['ver'] is True


def test_install_megamek_0422_with_correct_filename_and_type():
  assert install_megamek(idx=2, version='0.42.2'), \
  'Should return true when filename and path are both correct.'


def test_megatech_setup_with_installed_megamek_0422():
  assert mega2.setup(new_version='0.42.2')['ver'] is True

def test_install_megamek_with_incorrect_filename():
  with pytest.raises(FileNotFoundError, message='Should raise FileNotfoundError'):
    install_megamek(idx=3, version='foo')


def test_install_megamek_with_correct_filename_and_incorrect_type():
  # the file is called megamek-000.tar.gz, but it's a renamed zip file
  with pytest.raises(NotaTarFile, message='Should raise NotaTarFile, because it is a zip file.'):
    install_megamek(idx=3, version='000')


def test_install_megamek_with_reinstall_parameter():
  assert install_megamek(idx=1, version='0.44.0', reinstall=True), 'Should return true.'


# test for various directories that have to be
# in the newly installed megamek-[version] dir

def test_1_existence_of_directories_and_files_inside_megamek_0440_installation():
  mmdir = './mek/installed/1/megamek-0.44.0/' # was installed in the first test

  assert os.path.isfile(f'{mmdir}logs/megameklog.txt'), 'megameklog.txt file should exist'
  assert os.path.isdir(f'{mmdir}data/mechfiles/astech/'), 'astech dir should exist in mechfiles'
  assert os.path.isdir(f'{mmdir}data/boards/astech/'), 'astech dir should exist in boards'
  assert os.path.isdir(f'{mmdir}savegames/'), 'savegames dir should exist'


def test_2_existence_of_directories_and_files_inside_megamek_0422_installation():
  mmdir = './mek/installed/2/megamek-0.42.2/' # was installed in the second test

  assert os.path.isfile(f'{mmdir}logs/megameklog.txt'), 'megameklog.txt file should exist'
  assert os.path.isdir(f'{mmdir}data/mechfiles/astech/'), 'astech dir should exist in mechfiles'
  assert os.path.isdir(f'{mmdir}data/boards/astech/'), 'astech dir should exist in boards'
  assert os.path.isdir(f'{mmdir}savegames/'), 'savegames dir should exist'

