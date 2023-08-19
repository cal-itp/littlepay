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
    mock_Config.active_env_name.return_value = "env123"
    mock_Config.active_participant_id.return_value = ""

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, [no participant]" in capture.out


def test_configure_participant_credentials_empty(mock_Config, capfd):
    mock_Config.active_env_name.return_value = "env123"
    mock_Config.active_participant_id.return_value = "participant123"
    mock_Config.active_credentials.return_value = DEFAULT_CREDENTIALS

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123" in capture.out
    assert "[missing credentials]" in capture.out


def test_configure_participant_credentials_missing(mock_Config, capfd):
    mock_Config.active_env_name.return_value = "env123"
    mock_Config.active_participant_id.return_value = "participant123"
    mock_Config.active_credentials.side_effect = ValueError

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123 [missing credentials]" in capture.out


def test_configure_participant_credentials_None(mock_Config, capfd):
    mock_Config.active_env_name.return_value = "env123"
    mock_Config.active_participant_id.return_value = "participant123"
    mock_Config.active_credentials.return_value = None

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active: env123, participant123 [missing credentials]" in capture.out


def test_configure_participant_credentials_prod(mock_Config, capfd):
    mock_Config.active_env.return_value = {"url": "https://example.com"}
    mock_Config.active_env_name.return_value = ENV_PROD
    mock_Config.active_participant_id.return_value = "participant123"
    mock_Config.active_credentials.return_value = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Active: ⚠️  prod, participant123" in capture.out
    assert "[missing credentials]" not in capture.out
