from typing import Generator
import pytest

from littlepay.api import ListResponse
from littlepay.api.funding_sources import (
    FundingSourceDateFields,
    FundingSourceGroupResponse,
    FundingSourceResponse,
    FundingSourcesMixin,
)


@pytest.fixture
def ListResponse_FundingSourceGroups(expected_expiry_str):
    items = [
        dict(
            id="0",
            group_id="zero",
            label="label0",
            expiry_date=expected_expiry_str,
            created_date=expected_expiry_str,
            updated_date=expected_expiry_str,
        ),
        dict(
            id="1",
            group_id="one",
            label="label1",
            expiry_date=expected_expiry_str,
            created_date=expected_expiry_str,
            updated_date=expected_expiry_str,
        ),
        dict(id="2", group_id="two", label="label2", expiry_date="", created_date=""),
    ]
    return ListResponse(list=items, total_count=3)


@pytest.fixture
def mock_ClientProtocol_get_FundingResource(mocker, expected_expiry_str):
    funding_source = FundingSourceResponse(
        id="0",
        card_first_digits="0000",
        card_last_digits="0000",
        card_expiry_month="11",
        card_expiry_year="24",
        card_scheme="Visa",
        form_factor="unknown",
        participant_id="cst",
        is_fpan=True,
        related_funding_sources=[],
        created_date=expected_expiry_str,
    )
    return mocker.patch("littlepay.api.ClientProtocol._get", return_value=funding_source)


@pytest.fixture
def mock_ClientProtocol_get_list_FundingSourceGroup(mocker, ListResponse_FundingSourceGroups):
    return mocker.patch(
        "littlepay.api.ClientProtocol._get_list",
        side_effect=lambda *args, **kwargs: (g for g in ListResponse_FundingSourceGroups.list),
    )


def test_FundingSourceResponse_unexpected_fields():
    response_json = {
        "id": "0",
        "card_first_digits": "0000",
        "card_last_digits": "0000",
        "card_expiry_month": "11",
        "card_expiry_year": "24",
        "card_scheme": "Visa",
        "form_factor": "unknown",
        "participant_id": "cst",
        "is_fpan": True,
        "related_funding_sources": [],
        "unexpected_field": "test value",
    }

    # this test will fail if any error occurs from instantiating the class
    FundingSourceResponse.from_kwargs(**response_json)


def test_FundingSourceResponse_no_date_field():
    response_json = {
        "id": "0",
        "card_first_digits": "0000",
        "card_last_digits": "0000",
        "card_expiry_month": "11",
        "card_expiry_year": "24",
        "card_scheme": "Visa",
        "form_factor": "unknown",
        "participant_id": "cst",
        "is_fpan": True,
        "related_funding_sources": [],
    }

    funding_source = FundingSourceResponse.from_kwargs(**response_json)
    assert funding_source.created_date is None


def test_FundingSourceResponse_with_date_field(expected_expiry_str, expected_expiry):
    response_json = {
        "id": "0",
        "card_first_digits": "0000",
        "card_last_digits": "0000",
        "card_expiry_month": "11",
        "card_expiry_year": "24",
        "card_scheme": "Visa",
        "form_factor": "unknown",
        "participant_id": "cst",
        "is_fpan": True,
        "related_funding_sources": [],
        "created_date": expected_expiry_str,
    }

    funding_source = FundingSourceResponse.from_kwargs(**response_json)
    assert funding_source.created_date == expected_expiry


def test_FundingSourceDateFields(expected_expiry_str, expected_expiry):
    fields = FundingSourceDateFields(
        created_date=expected_expiry_str, updated_date=expected_expiry_str, expiry_date=expected_expiry_str
    )

    assert fields.created_date == expected_expiry
    assert fields.updated_date == expected_expiry
    assert fields.expiry_date == expected_expiry


def test_FundingSourceGroupResponse_unexpected_fields():
    response_json = {"id": "id", "group_id": "group_id", "label": "label", "unexpected_field": "test value"}

    # this test will fail if any error occurs from instantiating the class
    FundingSourceGroupResponse.from_kwargs(**response_json)


def test_FundingSourceGroupResponse_no_dates():
    response = FundingSourceGroupResponse(id="id", group_id="group_id", label="label")

    assert response.id == "id"
    assert response.group_id == "group_id"
    assert response.label == "label"
    assert response.created_date is None
    assert response.updated_date is None
    assert response.expiry_date is None


def test_FundingSourceGroupResponse_with_dates(expected_expiry_str, expected_expiry):
    response = FundingSourceGroupResponse(
        id="id",
        group_id="group_d",
        label="label",
        created_date=expected_expiry_str,
        updated_date=expected_expiry_str,
        expiry_date=expected_expiry_str,
    )

    assert response.created_date == expected_expiry
    assert response.updated_date == expected_expiry
    assert response.expiry_date == expected_expiry


def test_FundingSourcesMixin_funding_sources_by_token_endpoint(url):
    client = FundingSourcesMixin()

    assert client.funding_source_by_token_endpoint("abc_token") == f"{url}/fundingsources/bytoken/abc_token"


def test_FundingSourcesMixin_funding_source_concession_groups_endpoint(url):
    client = FundingSourcesMixin()

    assert (
        client.funding_source_concession_groups_endpoint("abd_funding_source")
        == f"{url}/fundingsources/abd_funding_source/concession_groups"
    )


def test_FundingSourcesMixin_get_funding_source_by_token(mock_ClientProtocol_get_FundingResource):
    client = FundingSourcesMixin()

    card_token = "abc"
    result = client.get_funding_source_by_token(card_token)

    mock_ClientProtocol_get_FundingResource.assert_called_once_with(
        client.funding_source_by_token_endpoint(card_token), FundingSourceResponse
    )
    assert isinstance(result, FundingSourceResponse)


def test_FundingSourcesMixin_get_concession_group_linked_funding_sources(
    ListResponse_FundingSourceGroups, mock_ClientProtocol_get_list_FundingSourceGroup, expected_expiry, expected_expiry_str
):
    client = FundingSourcesMixin()

    result = client.get_funding_source_linked_concession_groups("funding-source-1234")
    assert isinstance(result, Generator)
    assert mock_ClientProtocol_get_list_FundingSourceGroup.call_count == 0

    result_list = list(result)
    mock_ClientProtocol_get_list_FundingSourceGroup.assert_called_once_with(
        client.funding_source_concession_groups_endpoint("funding-source-1234"), per_page=100
    )

    expected_list = ListResponse_FundingSourceGroups.list

    assert len(result_list) == len(expected_list)
    assert all([isinstance(i, FundingSourceGroupResponse) for i in result_list])

    for i in range(len(result_list)):
        assert result_list[i].id == expected_list[i]["id"]
        assert result_list[i].group_id == expected_list[i]["group_id"]
        assert result_list[i].label == expected_list[i]["label"]

        if expected_list[i].get("expiry_date") == expected_expiry_str:
            assert result_list[i].expiry_date == expected_expiry
        else:
            assert result_list[i].expiry_date is None

        if expected_list[i].get("created_date") == expected_expiry_str:
            assert result_list[i].created_date == expected_expiry
        else:
            assert result_list[i].created_date is None

        if expected_list[i].get("updated_date") == expected_expiry_str:
            assert result_list[i].updated_date == expected_expiry
        else:
            assert result_list[i].updated_date is None
