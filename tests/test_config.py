from pathlib import Path

import pytest

from littlepay.config import (
    CONFIG_ACTIVE,
    CONFIG_ENV,
    CONFIG_ENVS,
    CONFIG_PARTICIPANT,
    CONFIG_PARTICIPANTS,
    DEFAULT_CONFIG,
    ENV_QA,
    all_envs,
    all_participants,
    get_config_path,
    get_config,
    active_env,
    active_participant,
)
from tests.conftest import CUSTOM_CONFIG_FILE


@pytest.fixture
def mock_get_config(mocker):
    return mocker.patch("littlepay.config.get_config")


def test_get_config_path_default(custom_config_file: Path):
    result = get_config_path()

    assert isinstance(result, Path)
    assert result == custom_config_file


def test_get_config_path_current(custom_current_file: Path):
    expected = "."
    custom_current_file.write_text(expected)

    result = get_config_path()

    assert result == Path(expected)


@pytest.mark.parametrize("path_arg", [None, "", CUSTOM_CONFIG_FILE, Path(CUSTOM_CONFIG_FILE)])
def test_get_config(path_arg, custom_current_file: Path, custom_config_file: Path):
    assert not custom_current_file.exists()
    assert not custom_config_file.exists()

    config = get_config(path_arg)

    assert custom_current_file.exists()
    current_config_path = Path(custom_current_file.read_text())

    assert current_config_path.resolve() == custom_config_file.resolve()
    assert custom_config_file.exists()
    assert config == DEFAULT_CONFIG


def test_get_config_exists(custom_config_file: Path):
    assert not custom_config_file.exists()
    custom_config_file.write_text("the config")
    assert custom_config_file.exists()

    config = get_config(custom_config_file)

    assert config == "the config"


def test_get_config_reset(custom_config_file: Path):
    assert not custom_config_file.exists()
    custom_config_file.write_text("the config")
    assert custom_config_file.exists()

    config = get_config(custom_config_file, reset=True)

    assert custom_config_file.exists()
    assert config == DEFAULT_CONFIG


def test_all_envs(mock_get_config):
    envs = {"one": "", "two": ""}
    mock_get_config.return_value = {CONFIG_ENVS: envs}
    result = all_envs()

    assert result == envs


def test_all_envs_config():
    envs = {"three": "", "four": ""}
    config = {CONFIG_ENVS: envs}
    result = all_envs(config)

    assert result == envs


def test_all_participants(mock_get_config):
    participants = {"one": "", "two": ""}
    mock_get_config.return_value = {CONFIG_PARTICIPANTS: participants}
    result = all_participants()

    assert result == participants


def test_all_participants_config():
    participants = {"three": "", "four": ""}
    config = {CONFIG_PARTICIPANTS: participants}
    result = all_participants(config)

    assert result == participants


def test_active_env(mocker):
    mocker.patch(
        "littlepay.config.get_config",
        return_value={CONFIG_ACTIVE: {CONFIG_ENV: "active_env"}, CONFIG_ENVS: {"active_env": "the active env"}},
    )
    result = active_env()

    assert result == ("active_env", "the active env")


def test_active_env_default(mock_get_config):
    mock_get_config.return_value = {CONFIG_ACTIVE: {}, CONFIG_ENVS: {ENV_QA: "the qa env"}}
    result = active_env()

    assert result == (ENV_QA, "the qa env")


def test_active_env_config():
    config = {CONFIG_ACTIVE: {CONFIG_ENV: "active_env"}, CONFIG_ENVS: {"active_env": "the active env"}}
    result = active_env(config)

    assert result == ("active_env", "the active env")


def test_active_participant(mock_get_config):
    mock_get_config.return_value = {
        CONFIG_ACTIVE: {CONFIG_PARTICIPANT: "participant123"},
        CONFIG_PARTICIPANTS: {"participant123": "the active participant"},
    }
    result = active_participant()

    assert result == ("participant123", "the active participant")


def test_active_participant_default(mock_get_config):
    mock_get_config.return_value = {CONFIG_ACTIVE: {}}
    result = active_participant()

    assert result == ("", {})


def test_active_participant_config():
    config = {
        CONFIG_ACTIVE: {CONFIG_PARTICIPANT: "participant456"},
        CONFIG_PARTICIPANTS: {"participant456": "the active participant"},
    }
    result = active_participant(config)

    assert result == ("participant456", "the active participant")
