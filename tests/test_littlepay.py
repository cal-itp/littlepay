import subprocess

from littlepay.commands import RESULT_SUCCESS


def test_littlepay(capfd):
    res = subprocess.call(["littlepay"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Env:" in capture.out
    assert res == RESULT_SUCCESS


def test_config(capfd):
    res = subprocess.call(["littlepay", "config"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Env:" in capture.out
    assert res == RESULT_SUCCESS
