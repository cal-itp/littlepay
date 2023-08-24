import time
from typing import Callable, TypeAlias

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import pytest

from littlepay.api.client import _client_from_active_config, _json_post_credentials, Client
from littlepay.config import Config


# type alias to give hints and help for fixture
# represents a function taking any arguments that returns a Client
ClientFunc: TypeAlias = Callable[..., Client]


@pytest.fixture
def make_client(url) -> ClientFunc:
    """A fixture returning a function that creates a Client, with additional kwargs passed through.

    Type annotation helps code completion and intellisense hinting in tests below.
    """

    def _make_client(**kwargs) -> Client:
        return Client(url, "client_id", "client_secret", "audience", **kwargs)

    return _make_client


@pytest.fixture
def mock_active_Config(mocker, credentials, token, url):
    new_credentials = dict(credentials)
    del new_credentials["grant_type"]
    config = mocker.Mock(wraps=Config())
    config.active_env = {"url": url, "version": "v1"}
    config.active_token = token
    config.active_credentials = new_credentials
    return config


def test_client_from_active_config(
    mock_active_Config, credentials, accept_header, content_type_header, url, user_agent_header
):
    client = _client_from_active_config(mock_active_Config)

    assert client.credentials == credentials
    assert client.base_url == url
    assert client.version == "v1"
    assert client.token_endpoint == f"{client.base_url}/api/{client.version}/oauth/token"
    assert accept_header in client.headers.items()
    assert content_type_header in client.headers.items()
    assert user_agent_header in client.headers.items()


def test_json_post_credentials(url):
    body = "one=1&two=2&three=%2F3"
    json = '{"one": "1", "two": "2", "three": "/3"}'

    result_uri, result_headers, result_json = _json_post_credentials(None, None, url, {}, body)

    assert result_uri == url
    assert result_headers["Content-Length"] == len(json)
    assert result_json == json


def test_Client(make_client: ClientFunc, credentials, accept_header, content_type_header, url, user_agent_header):
    client = make_client()

    assert client.credentials == credentials
    assert client.base_url == url
    assert client.version == "v1"
    assert client.token_endpoint == f"{client.base_url}/api/{client.version}/oauth/token"
    assert accept_header in client.headers.items()
    assert content_type_header in client.headers.items()
    assert user_agent_header in client.headers.items()


def test_Client_from_active_config(
    mock_active_Config, credentials, token, accept_header, content_type_header, user_agent_header, url
):
    client = Client.from_active_config(mock_active_Config)

    assert client.credentials == credentials
    assert client.base_url == url
    assert client.version == "v1"
    assert client.token_endpoint == f"{client.base_url}/api/{client.version}/oauth/token"
    assert client.oauth.token == token
    assert accept_header in client.headers.items()
    assert content_type_header in client.headers.items()
    assert user_agent_header in client.headers.items()


def test_Client_oauth(make_client: ClientFunc):
    client = make_client()

    assert isinstance(client.oauth, OAuth2Session)
    assert client.oauth.metadata == {"token_endpoint": client.token_endpoint}


def test_Client_token(make_client: ClientFunc, token):
    client = make_client(token=token)

    assert client.oauth.token == token
    assert client.token == token
    assert isinstance(client.token, OAuth2Token)


def test_Client_token_expired(mocker, make_client: ClientFunc, token):
    expired_token = dict(token)
    expiry = time.time() - 1000
    expired_token["expires_at"] = expiry

    client = make_client(token=expired_token)
    mocker.patch.object(client.oauth, "fetch_token", return_value=token)

    assert client.oauth.token is None
    assert client.token == token
    assert client.oauth.token == token


def test_Client_token_None(mocker, make_client: ClientFunc, token):
    client = make_client(token=None)
    mocker.patch.object(client.oauth, "fetch_token", return_value=token)

    assert client.oauth.token is None
    assert client.token == token
    assert client.oauth.token == token


def test_Client_version(make_client: ClientFunc, version):
    client = make_client(version=version)

    assert client.version == version


def test_Client_make_endpoint(make_client: ClientFunc, url):
    client = make_client()
    partial = "partial/123.json"

    result = client._make_endpoint(*partial.split("/"))

    assert result == f"{url}/api/v1/{partial}"


def test_Client_make_endpoint_version(make_client: ClientFunc, url, version):
    client = make_client(version=version)
    partial = "partial/123.json"

    result = client._make_endpoint(*partial.split("/"))

    assert result == f"{url}/api/{version}/{partial}"
