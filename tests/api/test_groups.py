from typing import Generator

import pytest

from littlepay.api.groups import GroupResponse, GroupsMixin


@pytest.fixture
def mock_ClientProtocol_get_list_Groups(mocker):
    items = [
        dict(id="0", label="zero", participant_id="zero_0"),
        dict(id="1", label="one", participant_id="one_1"),
        dict(id="2", label="two", participant_id="two_2"),
    ]
    return mocker.patch("littlepay.api.ClientProtocol._get_list", side_effect=lambda *args, **kwargs: (g for g in items))


@pytest.fixture
def mock_ClientProtocol_post(mocker):
    response = dict(id="0", participant_id="zero_0")
    return mocker.patch("littlepay.api.ClientProtocol._post", side_effect=lambda *args, **kwargs: response)


def test_GroupsMixin_concession_groups_endpoint(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint() == f"{url}/concession_groups"


def test_GroupsMixin_concession_groups_endpoint_group_id(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint("1234") == f"{url}/concession_groups/1234"


def test_GroupsMixin_concession_groups_endpoint_group_id_extras(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint("1234", "extra", "5678") == f"{url}/concession_groups/1234/extra/5678"


def test_GroupsMixin_create_concession_group(mock_ClientProtocol_post):
    client = GroupsMixin()

    result = client.create_concession_group("the-label")

    mock_ClientProtocol_post.assert_called_once_with(client.concession_groups_endpoint(), {"label": "the-label"}, dict)
    assert isinstance(result, dict)
    assert result["id"] == "0"
    assert result["participant_id"] == "zero_0"


def test_GroupsMixin_get_concession_groups(mock_ClientProtocol_get_list_Groups):
    client = GroupsMixin()

    result = client.get_concession_groups()
    assert isinstance(result, Generator)
    assert mock_ClientProtocol_get_list_Groups.call_count == 0

    result_list = list(result)
    mock_ClientProtocol_get_list_Groups.assert_called_once_with(client.concession_groups_endpoint())
    assert len(result_list) == 3
    assert all([isinstance(item, GroupResponse) for item in result_list])
    assert result_list[0].id == "0"
    assert result_list[0].label == "zero"
    assert result_list[0].participant_id == "zero_0"
    assert result_list[1].id == "1"
    assert result_list[1].label == "one"
    assert result_list[1].participant_id == "one_1"
    assert result_list[2].id == "2"
    assert result_list[2].label == "two"
    assert result_list[2].participant_id == "two_2"


def test_GroupsMixin_remove_concession_group(mock_ClientProtocol_delete):
    client = GroupsMixin()

    result = client.remove_concession_group("1234")

    mock_ClientProtocol_delete.assert_called_once_with(client.concession_groups_endpoint("1234"))
    assert result is True
