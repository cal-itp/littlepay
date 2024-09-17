import dataclasses
from json import JSONDecodeError
import time
from typing import Callable, Generator, TypeAlias

from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token
import pytest
from requests import HTTPError

from littlepay.api import ListResponse, from_kwargs
from littlepay.api.client import _client_from_active_config, _fix_bearer_token_header, _json_post_credentials, Client
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


@dataclasses.dataclass
class SampleResponse:
    one: str
    two: str
    three: int

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)


@pytest.fixture
def SampleResponse_json():
    return {"one": "single", "two": "double", "three": 3}


@pytest.fixture
def SampleResponse_json_with_unexpected_field():
    return {"one": "single", "two": "double", "three": 3, "four": "4"}


@pytest.fixture
def default_list_params():
    return dict(page=1, per_page=100)


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


@pytest.mark.parametrize(("current", "expected"), [("Bearer 1234", "1234"), ("1234", "1234")])
def test_fix_bearer_token_header(current, expected):
    headers = {"Authorization": current}

    _, headers, _ = _fix_bearer_token_header(None, headers, None)

    assert headers["Authorization"] == expected


def test_fix_bearer_token_header_no_Authorization(accept_header, content_type_header, user_agent_header):
    header_tuples = (accept_header, content_type_header, user_agent_header)
    headers = dict((key, val) for key, val in header_tuples)
    assert "Authorization" not in headers

    _, headers, _ = _fix_bearer_token_header(None, headers, None)

    assert "Authorization" not in headers
    assert headers[accept_header[0]] == accept_header[1]
    assert headers[content_type_header[0]] == content_type_header[1]
    assert headers[user_agent_header[0]] == user_agent_header[1]


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
    assert client.oauth.token_endpoint_auth_method == _json_post_credentials
    assert _fix_bearer_token_header in client.oauth.token_auth.hooks


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


def test_Client_delete(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=True))
    req_spy = mocker.patch.object(client.oauth, "delete", return_value=mock_response)

    result = client._delete(url)

    req_spy.assert_called_once_with(url, headers=client.headers)
    assert result is True


def test_Client_delete_error_status(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(raise_for_status=mocker.Mock(side_effect=HTTPError))
    req_spy = mocker.patch.object(client.oauth, "delete", return_value=mock_response)

    with pytest.raises(HTTPError):
        client._delete(url)

    req_spy.assert_called_once_with(url, headers=client.headers)


def test_Client_get(mocker, make_client: ClientFunc, url, SampleResponse_json):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=SampleResponse_json)
    )
    req_spy = mocker.patch.object(client.oauth, "get", return_value=mock_response)

    result = client._get(url, SampleResponse)

    req_spy.assert_called_once_with(url, headers=client.headers, params={})
    assert isinstance(result, SampleResponse)
    assert result.one == "single"
    assert result.two == "double"
    assert result.three == 3


def test_Client_get_params(mocker, make_client: ClientFunc, url, SampleResponse_json):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=SampleResponse_json)
    )
    req_spy = mocker.patch.object(client.oauth, "get", return_value=mock_response)

    result = client._get(url, SampleResponse, one=1, two=2, three="three")

    req_spy.assert_called_once_with(url, headers=client.headers, params=dict(one=1, two=2, three="three"))
    assert isinstance(result, SampleResponse)
    assert result.one == "single"
    assert result.two == "double"
    assert result.three == 3


def test_Client_get_response_has_unexpected_fields(
    mocker, make_client: ClientFunc, url, SampleResponse_json_with_unexpected_field
):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False),
        json=mocker.Mock(return_value=SampleResponse_json_with_unexpected_field),
    )
    req_spy = mocker.patch.object(client.oauth, "get", return_value=mock_response)

    result = client._get(url, SampleResponse)

    req_spy.assert_called_once_with(url, headers=client.headers, params={})
    assert isinstance(result, SampleResponse)
    assert result.one == "single"
    assert result.two == "double"
    assert result.three == 3
    assert not hasattr(result, "four")


def test_Client_get_error_status(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(raise_for_status=mocker.Mock(side_effect=HTTPError))
    req_spy = mocker.patch.object(client.oauth, "get", return_value=mock_response)

    with pytest.raises(HTTPError):
        client._get(url, SampleResponse)

    req_spy.assert_called_once_with(url, headers=client.headers, params={})


def test_ListResponse_unexpected_fields():
    response_json = {"list": [1, 2, 3], "total_count": 3, "unexpected_field": "test value"}

    # this test will fail if any error occurs from instantiating the class
    ListResponse.from_kwargs(**response_json)


def test_Client_get_list(mocker, make_client: ClientFunc, url, default_list_params, ListResponse_sample):
    client = make_client()
    req_spy = mocker.patch.object(client, "_get", return_value=ListResponse_sample)

    generator = client._get_list(url)
    assert isinstance(generator, Generator)
    assert req_spy.call_count == 0

    result = list(generator)

    req_spy.assert_called_once_with(url, ListResponse, **default_list_params)
    assert result == ListResponse_sample.list


def test_Client_get_list_paging(mocker, make_client: ClientFunc, url, default_list_params):
    page2_params = dict(default_list_params)
    page2_params["page"] = 2

    page3_params = dict(default_list_params)
    page3_params["page"] = 3

    list_response = ListResponse(list=[1, 2, 3], total_count=9)
    pages = [list_response, list_response, list_response]
    client = make_client()
    req_spy = mocker.patch.object(client, "_get", side_effect=pages)

    result = list(client._get_list(url))

    assert req_spy.call_count == 3
    assert result == [1, 2, 3, 1, 2, 3, 1, 2, 3]


def test_Client_make_endpoint(make_client: ClientFunc, url):
    client = make_client()
    partial = "partial/123.json"

    result = client._make_endpoint(*partial.split("/"))

    assert result == f"{url}/api/v1/{partial}"


def test_Client_make_endpoint_None(make_client: ClientFunc, url):
    client = make_client()
    parts = ("one", None, "two", None)

    result = client._make_endpoint(*parts)

    assert result == f"{url}/api/v1/one/two"


def test_Client_make_endpoint_version(make_client: ClientFunc, url, version):
    client = make_client(version=version)
    partial = "partial/123.json"

    result = client._make_endpoint(*partial.split("/"))

    assert result == f"{url}/api/{version}/{partial}"


def test_Client_post(mocker, make_client: ClientFunc, url, SampleResponse_json):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=SampleResponse_json)
    )
    req_spy = mocker.patch.object(client.oauth, "post", return_value=mock_response)

    data = {"data": "123"}
    result = client._post(url, data, SampleResponse)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert isinstance(result, SampleResponse)
    assert result.one == "single"
    assert result.two == "double"
    assert result.three == 3


def test_Client_post_default_cls(mocker, make_client: ClientFunc, url, SampleResponse_json):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=SampleResponse_json)
    )
    req_spy = mocker.patch.object(client.oauth, "post", return_value=mock_response)

    data = {"data": "123"}
    result = client._post(url, data)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert isinstance(result, dict)
    assert result["one"] == "single"
    assert result["two"] == "double"
    assert result["three"] == 3


def test_Client_post_empty_response(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(
        # json() throws a JSONDecodeError, simulating an empty response
        json=mocker.Mock(side_effect=JSONDecodeError("msg", "doc", 0)),
        # raise_for_status() returns None
        raise_for_status=mocker.Mock(return_value=False),
        # fake a 201 status_code
        status_code=201,
    )
    req_spy = mocker.patch.object(client.oauth, "post", return_value=mock_response)

    data = {"data": "123"}

    result = client._post(url, data, dict)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert result == {"status_code": 201}


def test_Client_post_error_status(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(raise_for_status=mocker.Mock(side_effect=HTTPError))
    req_spy = mocker.patch.object(client.oauth, "post", return_value=mock_response)

    data = {"data": "123"}

    with pytest.raises(HTTPError):
        client._post(url, data, dict)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)


def test_Client_put(mocker, make_client: ClientFunc, url, SampleResponse_json):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False), json=mocker.Mock(return_value=SampleResponse_json)
    )
    req_spy = mocker.patch.object(client.oauth, "put", return_value=mock_response)

    data = {"data": "123"}
    result = client._put(url, data, SampleResponse)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert isinstance(result, SampleResponse)
    assert result.one == "single"
    assert result.two == "double"
    assert result.three == 3


def test_Client_put_default_cls(mocker, make_client: ClientFunc, url, ListResponse_sample):
    client = make_client()
    mock_response = mocker.Mock(
        raise_for_status=mocker.Mock(return_value=False),
        json=mocker.Mock(return_value=dataclasses.asdict(ListResponse_sample)),
    )
    req_spy = mocker.patch.object(client.oauth, "put", return_value=mock_response)

    data = {"data": "123"}
    result = client._put(url, data)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert isinstance(result, ListResponse)
    assert result.total_count == ListResponse_sample.total_count
    assert len(result.list) == len(ListResponse_sample.list)

    for list_item in result.list:
        assert list_item == ListResponse_sample.list[result.list.index(list_item)]


def test_Client_put_empty_response(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(
        # json() throws a JSONDecodeError, simulating an empty response
        json=mocker.Mock(side_effect=JSONDecodeError("msg", "doc", 0)),
        # raise_for_status() returns None
        raise_for_status=mocker.Mock(return_value=False),
        # fake a 201 status_code
        status_code=201,
    )
    req_spy = mocker.patch.object(client.oauth, "put", return_value=mock_response)

    data = {"data": "123"}

    result = client._put(url, data, dict)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
    assert result == {"status_code": 201}


def test_Client_put_error_status(mocker, make_client: ClientFunc, url):
    client = make_client()
    mock_response = mocker.Mock(raise_for_status=mocker.Mock(side_effect=HTTPError))
    req_spy = mocker.patch.object(client.oauth, "put", return_value=mock_response)

    data = {"data": "123"}

    with pytest.raises(HTTPError):
        client._put(url, data, dict)

    req_spy.assert_called_once_with(url, headers=client.headers, json=data)
