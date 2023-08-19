from pathlib import Path

import pytest

import littlepay.config
from littlepay.config import DEFAULT_CONFIG, get_config_path, get_config


CUSTOM_CONFIG_FILE = "./tests/test.config.yaml"


@pytest.fixture(autouse=True)
def custom_config_file():
    """Fixture overrides littlepay.config.DEFAULT_CONFIG_FILE for the duration of a test, resetting it back at the end."""
    default = littlepay.config.DEFAULT_CONFIG_FILE

    custom = Path(CUSTOM_CONFIG_FILE)
    custom.unlink(missing_ok=True)
    littlepay.config.DEFAULT_CONFIG_FILE = custom

    yield littlepay.config.DEFAULT_CONFIG_FILE

    custom.unlink(missing_ok=True)
    littlepay.config.DEFAULT_CONFIG_FILE = default


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
