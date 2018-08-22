# astech_v2
Second version of Astech, very different from the first one, so new repository

# the tests
Test are passing. Kinda. They are simulating a scenario where Astech_v2 is freshly installed and get trough initial sql setup: prepare username and initial password, downloads and install specified MegaMek versions into correct directories.
To make them pass:
- delete megamek archives from mek/archives directory, except a zip file, which serve as acciddenatly wrong file in a wrong place,
- delete everything from mek/installed directory,
- delete config/config.db file.

I don't know why yet, but tests are failing when executed too quickly one ofter another. I assume that pytest doesn't wait enough time after completing one test file and moving on. To make them work, launh them in that order:
- pytest -vv tests/test_100_prepare_env_with_datainterface.py
- pytest -vv tests/test_101_megatech.py tests/test_110_download_megamek.py tests/test_120_install_megamek.py
- pytest -vv tests/test_130_megatech_checkinstall.py
- pytest -vv tests/test_140_server_controls.py

test_120_install_megamek is, by using os.remove, essentially doing "rm -fr" on some directories (tries to remove installed Megamek), so be very caferull if You, for some reason, like to make hard links to root inside project directory.

# the progress
I have the backend (datainterface and astech) working and tested. Now I'm doing a web part. web_engine serves as a web logic and now I have to make template files for all pages. You may see some similarities between web_engine and astech from the previous version, but the code has been clean up a little. It needs more work, but it's mostly done. 
