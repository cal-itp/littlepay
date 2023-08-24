from authlib.integrations.requests_client import OAuth2Session

from littlepay.api.client import Client


def test_Client():
    client = Client("https://example.com", "client_id", "client_secret", "audience")

    assert client.audience == "audience"
    assert client.env_api_url == "https://example.com"
    assert client.client_id == "client_id"
    assert client.client_secret == "client_secret"
    assert client.token_endpoint == f"{client.env_api_url}/oauth/token"


def test_Client_session():
    client = Client("https://example.com", "client_id", "client_secret", "audience")

    assert isinstance(client.session, OAuth2Session)
    assert client.session.metadata["audience"] == client.audience
    assert client.session.client_id == client.client_id
    assert client.session.client_secret == client.client_secret
    assert client.session.metadata["grant_type"] == "client_credentials"
    assert client.session.metadata["token_endpoint"] == client.token_endpoint


def test_Client_session_token():
    client = Client("https://example.com", "client_id", "client_secret", "audience", "token123")

    assert client.session.token == "token123"


def test_Client_session_token_None():
    client = Client("https://example.com", "client_id", "client_secret", "audience", None)

    assert client.session.token is None
