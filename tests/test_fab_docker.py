from fabdocker.docker import _check_local


def test_true_is_true():
    fabenv_local = {'docker_local': True}
    fabenv_non_local = {'docker_local': False}
    assert _check_local(True, fabenv_local) is True
    assert _check_local(None, fabenv_local) is True
    assert _check_local(False, fabenv_local) is False
    assert _check_local(True, fabenv_non_local) is True
    assert _check_local(None, fabenv_non_local) is False
    assert _check_local(False, fabenv_non_local) is False
