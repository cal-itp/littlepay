import json
from pathlib import Path

import pytest

from littlepay.config import Config
from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.switch import switch, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


@pytest.fixture(autouse=True)
def sample_config(custom_config_file: Path) -> dict:
    config = {
        "active": {"env": "e1", "participant": "p1"},
        "envs": {"e1": "", "e2": ""},
        "participants": {"p1": "", "p2": ""},
    }
    custom_config_file.write_text(json.dumps(config))
    return config


def test_switch_env(mock_commands_config):
    assert Config().active_env_name == "e1"
    assert Config().active_participant_id == "p1"
    res = switch(env="e2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert Config().active_env_name == "e2"
    assert Config().active_participant_id == "p1"


def test_switch_participant(mock_commands_config):
    assert Config().active_env_name == "e1"
    assert Config().active_participant_id == "p1"
    res = switch(participant="p2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert Config().active_env_name == "e1"
    assert Config().active_participant_id == "p2"


def test_switch_both(mock_commands_config):
    assert Config().active_env_name == "e1"
    assert Config().active_participant_id == "p1"

    res = switch(env="e2", participant="p2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert Config().active_env_name == "e2"
    assert Config().active_participant_id == "p2"


def test_switch_none():
    with pytest.raises(ValueError):
        switch()
