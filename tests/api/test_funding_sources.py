import pytest

from littlepay.api.funding_sources import (
    FundingSourceDateFields,
    FundingSourceGroupResponse,
    FundingSourceResponse,
    FundingSourcesMixin,
)


@pytest.fixture
def mock_ClientProtocol_get_FundingResource(mocker):
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
    )
    return mocker.patch("littlepay.api.ClientProtocol._get", return_value=funding_source)


def test_FundingSourceDateFields(expected_expiry_str, expected_expiry):
    fields = FundingSourceDateFields(
        created_date=expected_expiry_str, updated_date=expected_expiry_str, expiry_date=expected_expiry_str
    )

    assert fields.created_date == expected_expiry
    assert fields.updated_date == expected_expiry
    assert fields.expiry_date == expected_expiry


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


def test_FundingSourcesMixin_get_funding_source_by_token(mock_ClientProtocol_get_FundingResource):
    client = FundingSourcesMixin()

    card_token = "abc"
    result = client.get_funding_source_by_token(card_token)

    mock_ClientProtocol_get_FundingResource.assert_called_once_with(
        client.funding_source_by_token_endpoint(card_token), FundingSourceResponse
    )
    assert isinstance(result, FundingSourceResponse)
