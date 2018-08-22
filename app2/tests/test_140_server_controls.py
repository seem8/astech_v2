import pytest

import os
from time import sleep
from .. import astech

mega1 = astech.MegaTech(idx=1)
mega2 = astech.MegaTech(idx=2)


# ------ Launching MegaMek server without a password. --------
def test_1_megamek_startserver_without_password():
  assert mega1.startserver() is True, 'Should be True after launching MegaMek.'
  sleep(4) # let's give Java some time :)
  assert mega1.ison is True, 'Should be True as it is running now.'
  assert mega1.process.poll() is None, 'Should be None as process is running fine.'


def test_1_megamek_checkserver_if_megamek_server_is_runinng():
  assert mega1.checkserver() is True, 'Should be True if server is running.'
  assert mega1.ison is True, 'Should be True as it is running.'


def test_1_megamek_startserver_with_already_running_server():
  assert mega1.startserver() is False, 'Should be false if trying to start a running server.'


def test_1_is_logfile_written():
  assert os.stat(mega1.logfile).st_size > 1, 'Log file should have something.'
  assert len(mega1.loglines()) > 1, 'LogLines should return list of logfile lines.'
# --------------------------------------------------------


# ------ Launching MegaMek server with a password. --------
def test_2_megemek_startserver_with_password():
  mega2.game_password = 'urbiedurbie'
  assert mega2.startserver() is True, 'Should be True after launching MegaMek.'
  sleep(4) # let's give Java some time :)
  assert mega2.ison is True, 'Should be True as it is running now.'
  assert mega2.process.poll() is None, 'Should be None as process is running fine.'


def test_2_megamek_checkserver_if_megamek_server_is_runinng():
  assert mega2.checkserver() is True, 'Should be True if server is running.'


def test_2_is_logfile_written():
  assert os.stat(mega2.logfile).st_size > 1, 'Log file should have something.'
  assert len(mega2.loglines()) > 1, 'LogLines should return list of logfile lines.'


# -------- Turning both megamek instances off. ----------
def test_3_megamek_stoperver():
  assert mega1.stopserver() is True, 'Should be True after stopping MegaMek.'
  assert mega1.ison is False, 'Should be False as it is not running.'
  sleep(1)


def test_3_megamek_stoperver():
  assert mega2.stopserver() is True, 'Should be True after stopping MegaMek.'
  assert mega2.ison is False, 'Should be False as it is not running.'
  sleep(1)
# --------------------------------------------------------


def test_4_megamek_stopserver_that_is_not_running():
  assert mega2.stopserver() is False, 'Should be False if MegaMek is not running.'
  assert mega2.ison is False, 'Should be False as it is not running.'


def test_4_mega_checkserver_if_server_is_not_running():
  assert mega2.checkserver() is False, 'Should be False if server is not running.'

