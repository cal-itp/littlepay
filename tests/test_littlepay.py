import subprocess

from littlepay.commands import RESULT_FAILURE


def test_littlepay(capfd):
    res = subprocess.call(["littlepay"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert res == RESULT_FAILURE


def test_config(capfd):
    res = subprocess.call(["littlepay", "config"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert res == RESULT_FAILURE
