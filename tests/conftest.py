from datetime import datetime, timezone
from pathlib import Path

import pytest
from pytest_socket import disable_socket

from littlepay import __version__
from littlepay.api import ListResponse
import littlepay.config
from littlepay.commands import RESULT_SUCCESS


CUSTOM_CONFIG_FILE = "./tests/test.config.yaml"
CUSTOM_CURRENT_FILE = "./tests/.current"


def pytest_runtest_setup():
    disable_socket()


@pytest.fixture
def accept_header():
    return ("Accept", "application/json")


@pytest.fixture
def content_type_header():
    return ("Content-Type", "application/json")


@pytest.fixture
def credentials():
    return {
        "audience": "audience",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "grant_type": "client_credentials",
    }


@pytest.fixture
def token():
    return {"data": "token123"}


@pytest.fixture
def url():
    return "https://www.example.com"


@pytest.fixture
def user_agent_header():
    return ("User-Agent", f"cal-itp/littlepay:{__version__}")


@pytest.fixture
def version():
    return "v5000"


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
def mock_commands_groups(mock_module_name):
    """Fixture returns a function that patches commands.groups in a given module."""
    return mock_module_name("groups")


@pytest.fixture
def mock_commands_products(mock_module_name):
    """Fixture returns a function that patches commands.products in a given module."""
    return mock_module_name("products")


@pytest.fixture
def mock_commands_switch(mock_module_name):
    """Fixture returns a function that patches commands.switch in a given module."""
    return mock_module_name("switch")


@pytest.fixture
def mock_ClientProtocol_delete(mocker):
    return mocker.patch("littlepay.api.ClientProtocol._delete", side_effect=lambda *args, **kwargs: True)


@pytest.fixture(autouse=True)
def mock_ClientProtocol_make_endpoint(mocker, url):
    # patch _make_endpoint to create a endpoint for example.com
    mocker.patch(
        "littlepay.api.ClientProtocol._make_endpoint", side_effect=lambda *args: f"{url}/{'/'.join([a for a in args if a])}"
    )


@pytest.fixture
def ListResponse_sample():
    return ListResponse(list=[{"one": 1}, {"two": 2}, {"three": 3}], total_count=3)


@pytest.fixture
def expected_expiry():
    return datetime(2024, 3, 19, 22, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def expected_expiry_str(expected_expiry):
    return expected_expiry.strftime("%Y-%m-%dT%H:%M:%SZ")
