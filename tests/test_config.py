from pathlib import Path

import pytest

import littlepay.config
from littlepay.config import (
    DEFAULT_CONFIG,
    DEFAULT_CREDENTIALS,
    ENV_QA,
    _get_current_path,
    _read_config,
    _write_config,
    _update_current_path,
    Config,
)
from tests.conftest import CUSTOM_CONFIG_FILE


def test_get_current_path_default(custom_config_file: Path):
    result = _get_current_path()

    assert isinstance(result, Path)
    assert result == custom_config_file


def test_get_current_path_custom(custom_current_file: Path):
    expected = "."
    custom_current_file.write_text(expected)

    result = _get_current_path()

    assert result == Path(expected)


def test_get_current_path_newline(custom_current_file: Path):
    expected = "."
    custom_current_file.write_text(".\n")

    result = _get_current_path()

    assert result == Path(expected)


def test_update_current_path_str(custom_current_file: Path):
    assert not custom_current_file.exists()

    _update_current_path("/the/path")

    assert custom_current_file.read_text() == "/the/path"


def test_update_current_path_Path(custom_current_file: Path):
    assert not custom_current_file.exists()

    _update_current_path(Path("/the/path"))

    assert custom_current_file.read_text() == "/the/path"


def test_read_config(custom_config_file: Path):
    custom_config_file.write_text("config: the config")

    config = _read_config(custom_config_file)

    assert config == {"config": "the config"}


def test_write_config(custom_config_file: Path):
    assert not custom_config_file.exists()

    _write_config({"config": "the config"}, custom_config_file)

    text = custom_config_file.read_text().strip()
    assert text.startswith("config:")
    assert text.endswith("the config")


@pytest.mark.parametrize("path_arg", [None, "", CUSTOM_CONFIG_FILE, Path(CUSTOM_CONFIG_FILE)])
def test_Config(path_arg, custom_current_file: Path, custom_config_file: Path):
    assert not custom_current_file.exists()
    assert not custom_config_file.exists()

    config = Config(path_arg)

    assert custom_current_file.exists()
    current_config_path = Path(custom_current_file.read_text())

    assert current_config_path.resolve() == custom_config_file.resolve()
    assert custom_config_file.exists()
    assert config.active == DEFAULT_CONFIG["active"]
    assert config.envs == DEFAULT_CONFIG["envs"]
    assert config.participants == DEFAULT_CONFIG["participants"]
    assert not hasattr(config, "token")


def test_Config_exists(custom_config_file: Path):
    assert not custom_config_file.exists()
    custom_config_file.write_text('{"data": "the config", "other_data": "more config"}')
    assert custom_config_file.exists()

    config = Config(custom_config_file)

    assert config.data == "the config"
    assert config.other_data == "more config"


def test_Config_reset(custom_config_file: Path):
    assert not custom_config_file.exists()
    custom_config_file.write_text('{"data": "the config"}')
    assert custom_config_file.exists()

    config = Config(custom_config_file, reset=True)

    assert custom_config_file.exists()
    assert config.active == DEFAULT_CONFIG["active"]
    assert config.envs == DEFAULT_CONFIG["envs"]
    assert config.participants == DEFAULT_CONFIG["participants"]
    assert not hasattr(config, "data")


def test_Config_active_env_name(mocker):
    config = Config()
    config.active = mocker.Mock()
    config.active.get = mocker.Mock(return_value="active_env")

    assert config.active_env_name() == "active_env"


def test_Config_active_env_name_default():
    config = Config()
    config.active = {}

    assert config.active_env_name() == ENV_QA


def test_Config_active_env_name_update():
    config = Config()
    config.active = {"env": "original_env"}
    config.envs = {"original_env": "the original env", "new_env": "the new env"}

    result = config.active_env_name("new_env")

    assert result == "new_env"
    assert config.active_env_name() == result


def test_Config_active_env_name_update_unsupported(mocker):
    spy_write = mocker.spy(littlepay.config, "_write_config")
    config = Config()
    config.active = {"env": "original_env"}
    config.envs = {"original_env": "the original env"}

    with pytest.raises(ValueError):
        config.active_env_name("new_env")

    assert spy_write.call_count == 0
    assert config.active_env_name() == "original_env"


def test_Config_active_env():
    config = Config()
    config.active["env"] = "env123"
    config.envs["env123"] = "the environment"

    assert config.active_env() == "the environment"


def test_Config_active_participant_id(mocker):
    config = Config()
    config.active = mocker.Mock()
    config.active.get = mocker.Mock(return_value="active_participant")

    assert config.active_participant_id() == "active_participant"


def test_Config_active_participant_id_default():
    config = Config()
    config.active = {}

    assert config.active_participant_id() == ""


def test_Config_active_participant_id_update():
    config = Config()
    config.active = {"participant": "participant123"}
    config.participants = {"participant123": "one two three", "participant456": "four five six"}

    result = config.active_participant_id("participant456")

    assert result == "participant456"
    assert config.active_participant_id() == result


def test_Config_active_participant_id_update_unsupported(mocker):
    spy_write = mocker.spy(littlepay.config, "_write_config")
    config = Config()
    config.active = {"participant": "participant123"}
    config.participants = {"participant123": "one two three"}

    with pytest.raises(ValueError):
        config.active_participant_id("participant456")

    assert spy_write.call_count == 0
    assert config.active_participant_id() == "participant123"


def test_Config_active_participant():
    config = Config()
    config.active["env"] = "env123"
    config.active["participant"] = "participant123"
    config.participants = {"participant123": {"env123": "the participant config"}}

    assert config.active_participant() == "the participant config"


def test_Config_active_credentials_default(mocker):
    config = Config()
    mocker.patch.object(config, "active_participant", return_value={})

    credentials = config.active_credentials()

    assert credentials == {}


def test_Config_active_credentials_custom(mocker):
    custom = dict(**DEFAULT_CREDENTIALS)
    custom["client_id"] = "the ID"
    custom["client_secret"] = "123456"
    custom["audience"] = "the audience"

    config = Config()
    mocker.patch.object(config, "active_participant", return_value=custom)

    credentials = config.active_credentials()

    assert credentials == custom


def test_Config_active_credentials_missing(mocker):
    config = Config()
    mocker.patch.object(config, "active_participant", return_value={"env": "something", "data": "other"})

    credentials = config.active_credentials()

    assert credentials == {}


def test_Config_active_credentials_required(mocker):
    config = Config()
    mocker.patch.object(config, "active_participant", return_value=DEFAULT_CREDENTIALS)

    credentials = config.active_credentials(required=True)

    assert credentials == DEFAULT_CREDENTIALS


def test_Config_active_credentials_required_missing(mocker):
    config = Config()
    mocker.patch.object(config, "active_participant", return_value={})

    with pytest.raises(ValueError):
        config.active_credentials(required=True)
