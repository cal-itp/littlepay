from pathlib import Path
import subprocess

import pytest

from littlepay.commands import RESULT_SUCCESS
from littlepay.config import _get_current_path, _update_current_path
from tests.conftest import CUSTOM_CONFIG_FILE


@pytest.fixture(autouse=True)
def custom_config_file() -> Path:
    """Override fixture in conftest to temporarily use the CUSTOM_CONFIG_FILE as a "real" config file."""
    default = _get_current_path()

    custom = Path(CUSTOM_CONFIG_FILE)
    custom.unlink(missing_ok=True)
    _update_current_path(custom)

    yield custom

    custom.unlink(missing_ok=True)
    _update_current_path(default)


@pytest.fixture(autouse=True)
def custom_current_file() -> Path:
    """Override fixture in conftest to NOT return the test .current file, use the real one."""
    return


def test_littlepay(capfd):
    res = subprocess.call(["littlepay"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert res == RESULT_SUCCESS


def test_config(capfd):
    res = subprocess.call(["littlepay", "config"])
    capture = capfd.readouterr()

    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert res == RESULT_SUCCESS
