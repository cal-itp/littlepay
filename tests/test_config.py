from pathlib import Path

import pytest

import littlepay.config
from littlepay.config import (
    DEFAULT_CONFIG,
    DEFAULT_CREDENTIALS,
    _ensure_current_exists,
    _get_current_path,
    _read_config,
    _write_config,
    _update_current_path,
    Config,
)
from tests.conftest import CUSTOM_CONFIG_FILE


@pytest.fixture
def spy_ensure_current_exists(mocker):
    return mocker.spy(littlepay.config, "_ensure_current_exists")


def test_ensure_current_exists():
    # reminder: the module-level variable littlepay.config.CONFIG_FILE_CURRENT
    # is overwritten by the autouse fixture custom_current_file

    # the .current file should not exist to begin with
    assert not littlepay.config.CONFIG_FILE_CURRENT.exists()
    assert _ensure_current_exists() is False

    # now having ensured, the current file should exist
    assert littlepay.config.CONFIG_FILE_CURRENT.exists()
    # subsequent calls to ensure should indicate that it already exists
    assert _ensure_current_exists()


def test_get_current_path_default(custom_config_file: Path, spy_ensure_current_exists):
    result = _get_current_path()

    assert isinstance(result, Path)
    assert result.absolute() == custom_config_file.absolute()
    assert spy_ensure_current_exists.call_count > 0


def test_get_current_path_custom(custom_current_file: Path, spy_ensure_current_exists):
    expected = "."
    custom_current_file.write_text(expected)

    result = _get_current_path()

    assert result == Path(expected)
    assert spy_ensure_current_exists.call_count > 0


def test_get_current_path_newline(custom_current_file: Path, spy_ensure_current_exists):
    expected = "."
    custom_current_file.write_text(".\n")

    result = _get_current_path()

    assert result == Path(expected)
    assert spy_ensure_current_exists.call_count > 0


def test_update_current_path_str(custom_current_file: Path, spy_ensure_current_exists):
    assert not custom_current_file.exists()

    _update_current_path("/the/path")

    assert custom_current_file.read_text() == "/the/path"
    assert spy_ensure_current_exists.call_count > 0


def test_update_current_path_Path(custom_current_file: Path, spy_ensure_current_exists):
    assert not custom_current_file.exists()

    _update_current_path(Path("/the/path"))

    assert custom_current_file.read_text() == "/the/path"
    assert spy_ensure_current_exists.call_count > 0


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


def test_write_config_no_aliases_anchors(custom_config_file: Path):
    data = {"data1": "something", "data1": "something"}
    _write_config({"instance1": data, "instance2": data}, custom_config_file)

    text = custom_config_file.read_text().strip()
    assert "&id00" not in text
    assert "*id00" not in text


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


def test_Config_active_env_name(mocker):
    config = Config()
    config.active = {"env": "active_env"}

    assert config.active_env_name == "active_env"


def test_Config_active_env_name_default():
    config = Config()
    config.active = {}

    assert config.active_env_name == ""


def test_Config_active_env_name_update():
    config = Config()
    config.active = {"env": "original_env"}
    config.envs = {"original_env": "the original env", "new_env": "the new env"}

    config.active_env_name = "new_env"

    assert config.active_env_name == "new_env"
    assert Config().active_env_name == "new_env"


def test_Config_active_env_name_update_unsupported(mocker):
    spy_write = mocker.spy(littlepay.config, "_write_config")
    config = Config()
    config.active = {"env": "original_env"}
    config.envs = {"original_env": "the original env"}

    with pytest.raises(ValueError):
        config.active_env_name = "new_env"

    assert spy_write.call_count == 0
    assert config.active_env_name == "original_env"


def test_Config_active_env():
    config = Config()
    config.active = {"env": "env123"}
    config.envs = {"env123": "the environment"}

    assert config.active_env == "the environment"


def test_Config_active_missing():
    config = Config()
    config.active = {}
    config.envs = {"qa": "qa environment"}

    with pytest.raises(ValueError):
        config.active_env


def test_Config_active_participant_id(mocker):
    config = Config()
    config.active = {"participant": "active_participant"}

    assert config.active_participant_id == "active_participant"


def test_Config_active_participant_id_default():
    config = Config()
    config.active = {}

    assert config.active_participant_id == ""


def test_Config_active_participant_id_update():
    config = Config()
    config.active = {"participant": "participant123"}
    config.participants = {"participant123": "one two three", "participant456": "four five six"}

    config.active_participant_id = "participant456"

    assert config.active_participant_id == "participant456"
    assert Config().active_participant_id == "participant456"


def test_Config_active_participant_id_update_unsupported(mocker):
    spy_write = mocker.spy(littlepay.config, "_write_config")
    config = Config()
    config.active = {"participant": "participant123"}
    config.participants = {"participant123": "one two three"}

    with pytest.raises(ValueError):
        config.active_participant_id = "participant456"

    assert spy_write.call_count == 0
    assert config.active_participant_id == "participant123"


def test_Config_active_participant():
    config = Config()
    config.active = {"env": "env123", "participant": "participant123"}
    config.participants = {"participant123": {"env123": "the participant config"}}

    assert config.active_participant == "the participant config"


def test_Config_active_participant_missing():
    config = Config()
    config.active = {"env": "env123"}
    config.participants = {"participant123": {"env123": "the participant config"}}

    with pytest.raises(ValueError):
        config.active_participant


def test_Config_active_credentials_default(mocker):
    config = Config()
    mocker.patch("littlepay.config.Config.active_participant", new_callable=mocker.PropertyMock, return_value={})

    with pytest.raises(ValueError):
        config.active_credentials


def test_Config_active_credentials_custom(mocker):
    custom = dict(**DEFAULT_CREDENTIALS)
    custom["client_id"] = "the ID"
    custom["client_secret"] = "123456"
    custom["audience"] = "the audience"

    config = Config()
    mocker.patch("littlepay.config.Config.active_participant", new_callable=mocker.PropertyMock, return_value=custom)

    assert config.active_credentials == custom


def test_Config_active_credentials_missing(mocker):
    config = Config()
    mocker.patch(
        "littlepay.config.Config.active_participant",
        new_callable=mocker.PropertyMock,
        return_value={"env": "something", "data": "other"},
    )

    with pytest.raises(ValueError):
        config.active_credentials


def test_Config_active_token(mocker):
    token = {"data": "token123"}
    config = Config()
    mocker.patch("littlepay.config.Config.active_participant", new_callable=mocker.PropertyMock, return_value={"token": token})

    assert config.active_token == token


def test_Config_active_token_missing(mocker):
    config = Config()
    mocker.patch("littlepay.config.Config.active_participant", new_callable=mocker.PropertyMock, return_value={})

    assert config.active_token is None


def test_Config_active_token_update(mocker):
    mocker.patch("littlepay.config.Config.active_participant", new_callable=mocker.PropertyMock, return_value={})
    config = Config()
    assert config.active_token is None

    token = {"data": "token123"}
    config.active_token = token

    assert config.active_token == token
    assert config.active_participant["token"] == token

    assert Config().active_token == token
