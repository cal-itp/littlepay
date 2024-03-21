from datetime import datetime, timedelta, timezone
from typing import Generator

import pytest

from littlepay.api import ListResponse
from littlepay.api.groups import GroupFundingSourceResponse, GroupResponse, GroupsMixin


@pytest.fixture
def expected_expiry():
    return datetime(2024, 3, 19, 22, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def expected_expiry_str(expected_expiry):
    return expected_expiry.strftime("%Y-%m-%dT%H:%M:%SZ")


@pytest.fixture
def ListResponse_GroupFundingSources(expected_expiry_str):
    items = [
        dict(
            id="0",
            participant_id="zero_0",
            concession_expiry=expected_expiry_str,
            concession_created_at=expected_expiry_str,
            concession_updated_at=expected_expiry_str,
        ),
        dict(
            id="1",
            participant_id="one_1",
            concession_expiry=expected_expiry_str,
            concession_created_at=expected_expiry_str,
            concession_updated_at=expected_expiry_str,
        ),
        dict(id="2", participant_id="two_2", concession_expiry="", concession_created_at=""),
    ]
    return ListResponse(list=items, total_count=3)


@pytest.fixture
def mock_ClientProtocol_get_list_Groups(mocker):
    items = [
        dict(id="0", label="zero", participant_id="zero_0"),
        dict(id="1", label="one", participant_id="one_1"),
        dict(id="2", label="two", participant_id="two_2"),
    ]
    return mocker.patch("littlepay.api.ClientProtocol._get_list", side_effect=lambda *args, **kwargs: (g for g in items))


@pytest.fixture
def mock_ClientProtocol_get_list_FundingSources(mocker, ListResponse_GroupFundingSources):
    return mocker.patch(
        "littlepay.api.ClientProtocol._get_list",
        side_effect=lambda *args, **kwargs: (g for g in ListResponse_GroupFundingSources.list),
    )


@pytest.fixture
def mock_ClientProtocol_post_create_concession_group(mocker):
    response = dict(id="0", participant_id="zero_0")
    return mocker.patch("littlepay.api.ClientProtocol._post", side_effect=lambda *args, **kwargs: response)


@pytest.fixture
def mock_ClientProtocol_post_link_concession_group_funding_source(mocker):
    response = {"status_code": 201}
    return mocker.patch("littlepay.api.ClientProtocol._post", side_effect=lambda *args, **kwargs: response)


@pytest.fixture
def mock_ClientProtocol_put_update_concession_group_funding_source(mocker, ListResponse_GroupFundingSources):
    return mocker.patch(
        "littlepay.api.ClientProtocol._put", side_effect=lambda *args, **kwargs: ListResponse_GroupFundingSources
    )


def test_GroupResponse_csv():
    group = GroupResponse("id", "label", "participant")
    assert group.csv() == "id,label,participant"

    group = GroupResponse("id", "label, with, commas", "participant")
    assert group.csv() == 'id,"label, with, commas",participant'


def test_GroupResponse_csv_header():
    assert GroupResponse.csv_header() == "id,label,participant_id"


def test_GroupFundingSourceResponse_no_dates():
    response = GroupFundingSourceResponse("id", "participant_id")

    assert response.id == "id"
    assert response.participant_id == "participant_id"
    assert response.concession_expiry is None
    assert response.concession_created_at is None
    assert response.concession_updated_at is None


def test_GroupFundingSourceResponse_empty_dates():
    response = GroupFundingSourceResponse("id", "participant_id", "", "", "")

    assert response.id == "id"
    assert response.participant_id == "participant_id"
    assert response.concession_expiry is None
    assert response.concession_created_at is None
    assert response.concession_updated_at is None


def test_GroupFundingSourceResponse_with_dates(expected_expiry, expected_expiry_str):
    response = GroupFundingSourceResponse(
        "id", "participant_id", expected_expiry_str, expected_expiry_str, expected_expiry_str
    )

    assert response.id == "id"
    assert response.participant_id == "participant_id"
    assert response.concession_expiry == expected_expiry
    assert response.concession_expiry.tzinfo == timezone.utc
    assert response.concession_created_at == expected_expiry
    assert response.concession_created_at.tzinfo == timezone.utc
    assert response.concession_updated_at == expected_expiry
    assert response.concession_updated_at.tzinfo == timezone.utc


def test_GroupsMixin_concession_groups_endpoint(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint() == f"{url}/concession_groups"


def test_GroupsMixin_concession_groups_endpoint_group_id(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint("1234") == f"{url}/concession_groups/1234"


def test_GroupsMixin_concession_groups_endpoint_group_id_extras(url):
    client = GroupsMixin()

    assert client.concession_groups_endpoint("1234", "extra", "5678") == f"{url}/concession_groups/1234/extra/5678"


def test_GroupsMixin_concession_groups_funding_sources_endpoint(url):
    client = GroupsMixin()

    assert client.concession_group_funding_source_endpoint("1234") == f"{url}/concession_groups/1234/fundingsources"


def test_GroupsMixin_create_concession_group(mock_ClientProtocol_post_create_concession_group):
    client = GroupsMixin()

    result = client.create_concession_group("the-label")

    mock_ClientProtocol_post_create_concession_group.assert_called_once_with(
        client.concession_groups_endpoint(), {"label": "the-label"}, dict
    )
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


def test_GroupsMixin_get_concession_group_linked_funding_sources(
    ListResponse_GroupFundingSources, mock_ClientProtocol_get_list_FundingSources, expected_expiry, expected_expiry_str
):
    client = GroupsMixin()

    result = client.get_concession_group_linked_funding_sources("group-1234")
    assert isinstance(result, Generator)
    assert mock_ClientProtocol_get_list_FundingSources.call_count == 0

    result_list = list(result)
    mock_ClientProtocol_get_list_FundingSources.assert_called_once_with(
        client.concession_group_funding_source_endpoint("group-1234")
    )

    expected_list = ListResponse_GroupFundingSources.list

    assert len(result_list) == len(expected_list)
    assert all([isinstance(i, GroupFundingSourceResponse) for i in result_list])

    for i in range(len(result_list)):
        assert result_list[i].id == expected_list[i]["id"]
        assert result_list[i].participant_id == expected_list[i]["participant_id"]

        if expected_list[i].get("concession_expiry") == expected_expiry_str:
            assert result_list[i].concession_expiry == expected_expiry
        else:
            assert result_list[i].concession_expiry is None

        if expected_list[i].get("concession_created_at") == expected_expiry_str:
            assert result_list[i].concession_created_at == expected_expiry
        else:
            assert result_list[i].concession_created_at is None

        if expected_list[i].get("concession_updated_at") == expected_expiry_str:
            assert result_list[i].concession_updated_at == expected_expiry
        else:
            assert result_list[i].concession_updated_at is None


def test_GroupsMixin_link_concession_group_funding_source(mock_ClientProtocol_post_link_concession_group_funding_source):
    client = GroupsMixin()
    result = client.link_concession_group_funding_source("group-1234", "funding-source-1234")

    endpoint = client.concession_group_funding_source_endpoint("group-1234")
    mock_ClientProtocol_post_link_concession_group_funding_source.assert_called_once_with(
        endpoint, {"id": "funding-source-1234"}, dict
    )
    assert result == {"status_code": 201}


def test_GroupsMixin_format_concession_expiry_not_datetime(expected_expiry_str):
    client = GroupsMixin()
    with pytest.raises(TypeError, match="concession_expiry must be a Python datetime instance"):
        client._format_concession_expiry(expected_expiry_str)


def test_GroupsMixin_format_concession_expiry_aware_utc(expected_expiry, expected_expiry_str):
    client = GroupsMixin()
    result = client._format_concession_expiry(expected_expiry)

    assert result == expected_expiry_str


def test_GroupsMixin_format_concession_expiry_aware_not_utc():
    # construct a datetime in UTC-7 and the expected string formatting
    concession_expiry = datetime(2024, 3, 18, 1, 2, 3, tzinfo=timezone(timedelta(hours=-7)))
    expected_body_expiry = "2024-03-18T08:02:03Z"

    client = GroupsMixin()
    result = client._format_concession_expiry(concession_expiry)

    assert result == expected_body_expiry


def test_GroupsMixin_format_concession_expiry_naive():
    # construct a naive datetime and the expected string formatting
    concession_expiry = datetime(2024, 3, 18, 1, 2, 3, tzinfo=None)
    expected_body_expiry = "2024-03-18T01:02:03Z"

    client = GroupsMixin()
    result = client._format_concession_expiry(concession_expiry)

    assert result == expected_body_expiry


def test_GroupsMixin_link_concession_group_funding_source_expiry(
    mock_ClientProtocol_post_link_concession_group_funding_source, mocker
):
    client = GroupsMixin()
    mocker.patch.object(client, "_format_concession_expiry", return_value="formatted concession expiry")

    result = client.link_concession_group_funding_source("group-1234", "funding-source-1234", datetime.now())

    endpoint = client.concession_group_funding_source_endpoint("group-1234")
    mock_ClientProtocol_post_link_concession_group_funding_source.assert_called_once_with(
        endpoint, {"id": "funding-source-1234", "concession_expiry": "formatted concession expiry"}, dict
    )
    assert result == {"status_code": 201}


def test_GroupsMixin_update_concession_group_funding_source_expiry(
    mock_ClientProtocol_put_update_concession_group_funding_source, ListResponse_GroupFundingSources, mocker
):
    client = GroupsMixin()
    mocker.patch.object(client, "_format_concession_expiry", return_value="formatted concession expiry")

    result = client.update_concession_group_funding_source_expiry("group-1234", "funding-source-1234", datetime.now())

    endpoint = client.concession_group_funding_source_endpoint("group-1234")
    mock_ClientProtocol_put_update_concession_group_funding_source.assert_called_once_with(
        endpoint, {"id": "funding-source-1234", "concession_expiry": "formatted concession expiry"}, ListResponse
    )

    expected = GroupFundingSourceResponse(**ListResponse_GroupFundingSources.list[0])
    assert result == expected
