import pytest

from littlepay.api.funding_sources import FundingSourceDateFields, FundingSourceResponse, FundingSourcesMixin


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
