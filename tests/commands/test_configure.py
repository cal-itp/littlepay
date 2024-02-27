import pytest

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.commands.configure import configure
from littlepay.config import DEFAULT_CREDENTIALS, ENV_PROD, ENV_QA


@pytest.fixture
def mock_Client(mocker):
    return mocker.patch("littlepay.commands.configure.Client")


@pytest.fixture
def mock_Client_instance(mock_Client):
    return mock_Client.return_value


@pytest.fixture
def mock_Config(mocker):
    return mocker.patch("littlepay.commands.configure.Config").return_value


def test_configure(mocker, custom_config_file, capfd):
    assert not custom_config_file.exists()
    mocker.patch("littlepay.config._read_config", return_value={})

    res = configure(custom_config_file)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert custom_config_file.exists()
    assert "Config:" in capture.out
    assert "Envs:" in capture.out
    assert "Participants:" in capture.out
    assert "Active:" in capture.out
    assert "[no participant]" in capture.out


def test_configure_default(mock_Config, capfd):
    mock_Config.active_env_name = "env123"
    mock_Config.active_participant_id = ""

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
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
    # mocking a property and getting it to raise an exception, difficult!
    # https://stackoverflow.com/a/13353458/453168
    type(mock_Config).active_credentials = mocker.PropertyMock(side_effect=ValueError)

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


def test_configure_participant_credentials_misconfigured(mock_Client, mock_Config, capfd):
    mock_Config.active_env = {"url": "https://example.com"}
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}
    mock_Config.active_token = None
    mock_Client.from_active_config.return_value.token = None

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "[misconfigured credentials]" in capture.out


def test_configure_participant_credentials_qa(mock_Client_instance, mock_Config, capfd):
    mock_Config.active_env = {"url": "https://example.com"}
    mock_Config.active_env_name = ENV_QA
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}
    mock_Client_instance.token = {"data": "token123"}

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Active: qa, participant123" in capture.out
    assert "[misconfigured credentials]" not in capture.out
    assert "[missing credentials]" not in capture.out


def test_configure_participant_credentials_prod(mock_Client_instance, mock_Config, capfd):
    mock_Config.active_env = {"url": "https://example.com"}
    mock_Config.active_env_name = ENV_PROD
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}
    mock_Client_instance.token = {"data": "token123"}

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Active: ⚠️  prod, participant123" in capture.out
    assert "[misconfigured credentials]" not in capture.out
    assert "[missing credentials]" not in capture.out


def test_configure_participant_credentials_token_expiry(mocker, mock_Client_instance, mock_Config, capfd):
    mock_Config.active_env = {"url": "https://example.com"}
    mock_Config.active_env_name = ENV_PROD
    mock_Config.active_participant_id = "participant123"
    mock_Config.active_credentials = {k: "something" for k, _ in DEFAULT_CREDENTIALS.items()}

    mock_token = mocker.Mock(token={"expires_at": 1692926100})
    mock_ClientClass = mocker.patch("littlepay.commands.configure.Client")
    mock_ClientClass.from_active_config.return_value = mock_token

    res = configure()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Token expires: 2023-08-25T01:15:00" in capture.out
