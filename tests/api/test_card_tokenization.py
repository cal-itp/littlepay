from authlib.oauth2.rfc6749 import OAuth2Token

import pytest

from littlepay.api.card_tokenization import CardTokenizationMixin


@pytest.fixture
def token():
    return {"access_token": "1234"}


@pytest.fixture
def mock_ClientProtocol_post(mocker, token):
    return mocker.patch("littlepay.api.ClientProtocol._post", return_value=token)


def test_CardTokenizationMixin_card_tokenization_request_access_endpoint(url):
    client = CardTokenizationMixin()

    assert client.card_tokenization_request_access_endpoint() == f"{url}/cardtokenisation/requestaccess"


def test_CardTokenizationMixin_request_card_tokenization_access(mock_ClientProtocol_post):
    client = CardTokenizationMixin()

    token = client.request_card_tokenization_access()

    mock_ClientProtocol_post.assert_called_once_with(
        client.card_tokenization_request_access_endpoint(), {"request_access": "CARD_TOKENISATION"}
    )
    assert isinstance(token, OAuth2Token)
