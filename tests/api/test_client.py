import time

from requests import PreparedRequest, Session

from littlepay.api.client import _current_time, Client


def test_current_time():
    assert _current_time() == int(time.time())


def test_Client():
    client = Client("https://example.com", "client_id", "client_secret", "audience")

    assert client.credentials == {
        "audience": "audience",
        "client_id": "client_id",
        "client_secret": "client_secret",
        "grant_type": "client_credentials",
    }
    assert client.env_api_url == "https://example.com"
    assert client.env_api_version == "v1"
    assert client.token_endpoint == f"{client.env_api_url}/api/{client.env_api_version}/oauth/token"
    assert isinstance(client.token_refresh_request, PreparedRequest)
    assert client.token_refresh_request.method == "POST"
    assert client.token_refresh_request.url == client.token_endpoint


def test_Client_session():
    client = Client("https://example.com", "client_id", "client_secret", "audience")

    assert isinstance(client.session, Session)
    assert ("Accept", "application/json") in client.session.headers.items()
    assert ("Content-Type", "application/json") in client.session.headers.items()
    assert client.session.headers["User-Agent"].startswith("cal-itp/littlepay")


def test_Client_token(mocker):
    mocker.patch("littlepay.api.client.Client.current_time", return_value=100)
    client = Client("https://example.com", "client_id", "client_secret", "audience", token={"expires_in": 300})

    assert client._token == {"expires_in": 300}
    assert client._token_time == 100
    assert client.token_valid


def test_Client_token_None(mocker):
    mocker.patch("littlepay.api.client.Client.current_time", return_value=100)
    client = Client("https://example.com", "client_id", "client_secret", "audience", token=None)
    client.session = mocker.Mock(
        send=mocker.Mock(return_value=mocker.Mock(json=mocker.Mock(return_value={"expires_in": 300})))
    )

    assert client._token is None
    assert client._token_time == 0
    assert not client.token_valid

    token = client.token

    assert token == {"expires_in": 300}
    assert client._token == token
    assert client._token_time == 100
    assert client.token_valid


def test_Client_version():
    client = Client("https://example.com", "client_id", "client_secret", "audience", env_api_version="env_ver")

    assert client.env_api_version == "env_ver"


def test_Client_version_endpoint():
    client = Client("https://example.com", "client_id", "client_secret", "audience")
    partial = "partial/123.json"

    result = client._version_endpoint(partial)

    assert result == f"https://example.com/api/v1/{partial}"


def test_Client_version_endpoint_version():
    version = "env_ver"
    client = Client("https://example.com", "client_id", "client_secret", "audience", env_api_version=version)
    partial = "partial/123.json"

    result = client._version_endpoint(partial)

    assert result == f"https://example.com/api/{version}/{partial}"
