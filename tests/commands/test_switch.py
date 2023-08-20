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
    res = switch(switch_type="env", switch_arg="e2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert Config().active_env_name != "e1"
    assert Config().active_env_name == "e2"


def test_switch_participant(mock_commands_config):
    assert Config().active_participant_id == "p1"
    res = switch(switch_type="participant", switch_arg="p2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert Config().active_participant_id != "p1"
    assert Config().active_participant_id == "p2"


def test_switch_unrecognized_type(mock_commands_config):
    env = Config().active_env_name
    participant = Config().active_participant_id

    with pytest.raises(ValueError):
        switch(switch_type="unrecognized", switch_arg="new_value")

    assert Config().active_env_name == env
    assert Config().active_participant_id == participant
    assert mock_commands_config.call_count == 0
