import pytest
import urllib, shutil, tarfile
from time import sleep

from ..astech import download_megamek, WrongMegamekUrl, WrongMegamekFileName

# astech.download_megamek downloads megamek-[version].tar.gz file
# from githubproject page to provided [directory]


def test_download_megamek_with_correct_version_and_filename_with_redownload():
  assert download_megamek(version='0.44.0', redownload=True), 'Should return True'


def test_download_megamek_with_correct_version_and_filename_without_redownload():
  assert download_megamek(version='0.44.0'), 'Should return True'


def test_download_megamek_with_glitched_version_0422():
  assert download_megamek(version='0.42.2'), 'Should return True'


def test_download_megamek_with_incorrect_version_and_correct_filename():
  with pytest.raises(WrongMegamekUrl, message='Should raise WrongMegamekUrl'):
    download_megamek(version='foo')

def test_download_megamek_with_correct_version_and_incorrect_filename():
  with pytest.raises(WrongMegamekFileName, message='Should raise WrongMegamekFileName'):
    download_megamek(version='0.44.0', directory='./foo')


def test_download_megamek_with_incorrect_version_and_incorrect_filename():
  # in download_megamek WrongMegamekUrl error is raised first
  with pytest.raises(WrongMegamekUrl, message='Should raise WrongMegamekUrl'):
    download_megamek(version='foo', directory='./foo')



