import json
from pathlib import Path

import pytest

from littlepay.config import active_env, active_participant
from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.switch import switch, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


@pytest.fixture(autouse=True)
def sample_config(custom_config_file: Path) -> dict:
    config = {"active": {"env": "e1", "participant": "p1"}, "envs": {"e1": "", "e2": ""}, "participants": {"p1": "", "p2": ""}}
    custom_config_file.write_text(json.dumps(config))
    return config


def test_switch_env(mock_commands_config):
    assert "e1" in active_env()
    res = switch(switch_type="env", switch_arg="e2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert "e1" not in active_env()
    assert "e2" in active_env()


def test_switch_participant(mock_commands_config):
    assert "p1" in active_participant()
    res = switch(switch_type="participant", switch_arg="p2")

    assert res == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with()
    assert "p1" not in active_participant()
    assert "p2" in active_participant()


def test_switch_unrecognized_type(mock_commands_config):
    env = active_env()
    participant = active_participant()

    with pytest.raises(ValueError):
        switch(switch_type="unrecognized", switch_arg="new_value")

    assert active_env() == env
    assert active_participant() == participant
    assert mock_commands_config.call_count == 0
