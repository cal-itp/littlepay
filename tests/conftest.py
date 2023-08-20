from pathlib import Path

import pytest

import littlepay.config
from littlepay.commands import RESULT_SUCCESS


CUSTOM_CONFIG_FILE = "./tests/test.config.yaml"
CUSTOM_CURRENT_FILE = "./tests/.current"


@pytest.fixture(autouse=True)
def custom_config_file() -> Path:
    """Fixture overrides littlepay.config.DEFAULT_CONFIG_FILE for the duration of a test, resetting it back at the end."""
    default = littlepay.config.DEFAULT_CONFIG_FILE

    custom = Path(CUSTOM_CONFIG_FILE)
    custom.unlink(missing_ok=True)
    littlepay.config.DEFAULT_CONFIG_FILE = custom

    yield littlepay.config.DEFAULT_CONFIG_FILE

    custom.unlink(missing_ok=True)
    littlepay.config.DEFAULT_CONFIG_FILE = default


@pytest.fixture(autouse=True)
def custom_current_file() -> Path:
    """Fixture overrides littlepay.config.CONFIG_FILE_CURRENT for the duration of a test, resetting it back at the end."""
    default = littlepay.config.CONFIG_FILE_CURRENT

    custom = Path(CUSTOM_CURRENT_FILE)
    custom.unlink(missing_ok=True)
    littlepay.config.CONFIG_FILE_CURRENT = custom

    yield littlepay.config.CONFIG_FILE_CURRENT

    custom.unlink(missing_ok=True)
    littlepay.config.CONFIG_FILE_CURRENT = default


@pytest.fixture
def mock_module_name(mocker):
    """Fixture returns a function taking a name, that returns a function taking a module,
    patching the given name in the given module.

    By default, the patched object is given a return_value = RESULT_SUCCESS.
    """

    def _mock_module_name(name):
        def __mock_module_name(module):
            patched = mocker.patch(f"{module}.{name}")
            patched.return_value = RESULT_SUCCESS
            return patched

        return __mock_module_name

    return _mock_module_name


@pytest.fixture
def mock_commands_config(mock_module_name):
    """Fixture returns a function that patches commands.configure in a given module."""
    return mock_module_name("configure")


@pytest.fixture
def mock_commands_switch(mock_module_name):
    """Fixture returns a function that patches commands.switch in a given module."""
    return mock_module_name("switch")
