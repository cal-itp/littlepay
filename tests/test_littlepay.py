import subprocess

from littlepay import __version__ as version
from littlepay.commands import RESULT_SUCCESS


def test_littlepay(capfd):
    # call CLI command as a subprocess
    res = subprocess.call(["littlepay"])
    captured = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert f"littlepay: {version}" in captured.out
