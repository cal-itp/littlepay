import pytest

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.commands.configure import configure
from littlepay.config import DEFAULT_CREDENTIALS, ENV_PROD


@pytest.fixture
def mock_Config(mocker):
    return mocker.patch("littlepay.commands.configure.Config").return_value


def test_configure(mocker, custom_config_file, capfd):
    assert not custom_config_file.exists()
    mocker.patch("littlepay.config._read_config", return_value={})

    res = configure(custom_config_file)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert custom_config_file.exists()
    assert "Config:" in capture.out
    assert "Env:" in capture.out
    assert "[no participant]" in capture.out


def test_configure_default(mock_Config, capfd):
    mock_Config.active_env_name = "env123"
    mock_Config.active_participant_id = ""

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, [no participant]" in capture.out


def test_configure_participant_credentials_empty(mock_Config, capfd):
    mock_Config.active_env_name = "env123"
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = DEFAULT_CREDENTIALS

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123" in capture.out
    assert "[missing credentials]" in capture.out


def test_configure_participant_credentials_missing(mocker, mock_Config, capfd):
    mock_Config.active_env_name = "env123"
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {"client_id": "", "client_secret": "something", "audience": ""}

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123 [missing credentials]" in capture.out


def test_configure_participant_credentials_None(mock_Config, capfd):
    mock_Config.active_env_name = "env123"
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = None

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123 [missing credentials]" in capture.out


def test_configure_participant_credentials_prod(mock_Config, capfd):
    mock_Config.active_env = {"url": "https://example.com"}
    mock_Config.active_env_name = ENV_PROD
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Active: ⚠️  prod, participant123" in capture.out
    assert "[missing credentials]" not in capture.out
