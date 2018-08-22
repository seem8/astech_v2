import pytest

from ..astech import uninstall_megamek, WrongMegamekVersion

# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# ! BEWARE: if you have a link to ~ dir inside megamek,  !
# ! you'll LOOSE ALL DATA                                !
# ! (no, I haven't tried, but I'm pretty sure)           !
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

def test_uninstall_megamek_with_installed_version_of_megamek():
  assert uninstall_megamek(version='0.44.0') == True, 'Should return True after succesfull removal.'
  assert uninstall_megamek(version='0.42.2') == True, 'Should return True after succesfull removal.'


def test_unistall_megamek_with_bogus_version_of_megamek():
  with pytest.raises(WrongMegamekVersion, message='Should raise WrongMegamekVersion with bad version parameter.'):
    assert uninstall_megamek(version='foo')



