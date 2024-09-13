from datetime import datetime
from typing import Generator, List

from littlepay.api import ClientProtocol


class FundingSourceResponse:
    def __init__(
        self,
        id: str,
        card_first_digits: str,
        card_last_digits: str,
        card_expiry_month: str,
        card_expiry_year: str,
        card_scheme: str,
        form_factor: str,
        participant_id: str,
        is_fpan: bool,
        related_funding_sources: List[dict],
        card_category: str = None,
        issuer_country_code: str = None,
        issuer_country_numeric_code: str = None,
        replacement_funding_source: str = None,
        token: str = None,
        token_key_id: str = None,
        icc_hash: str = None,
        **kwargs,
    ):
        self.id = id
        self.card_first_digits = card_first_digits
        self.card_last_digits = card_last_digits
        self.card_expiry_month = card_expiry_month
        self.card_expiry_year = card_expiry_year
        self.card_scheme = card_scheme
        self.form_factor = form_factor
        self.participant_id = participant_id
        self.is_fpan = is_fpan
        self.related_funding_sources = related_funding_sources
        self.card_category = card_category
        self.issuer_country_code = issuer_country_code
        self.issuer_country_numeric_code = issuer_country_numeric_code
        self.replacement_funding_source = replacement_funding_source
        self.token = token
        self.token_key_id = token_key_id
        self.icc_hash = icc_hash


class FundingSourceDateFields:
    """Implements parsing of datetime strings to Python datetime objects for funding source fields."""

    def __init__(self, created_date: datetime = None, updated_date: datetime = None, expiry_date: datetime = None):
        """Parses any date parameters into Python datetime objects.

        For @dataclasses with a generated __init__ function, this function is called automatically.

        Includes a workaround for Python 3.10 where datetime.fromisoformat() can only parse the format output
        by datetime.isoformat(), i.e. without a trailing 'Z' offset character and with UTC offset expressed
        as +/-HH:mm

        https://docs.python.org/3.11/library/datetime.html#datetime.datetime.fromisoformat
        """
        if created_date:
            self.created_date = datetime.fromisoformat(created_date.replace("Z", "+00:00", 1))
        else:
            self.created_date = None

        if updated_date:
            self.updated_date = datetime.fromisoformat(updated_date.replace("Z", "+00:00", 1))
        else:
            self.updated_date = None

        if expiry_date:
            self.expiry_date = datetime.fromisoformat(expiry_date.replace("Z", "+00:00", 1))
        else:
            self.expiry_date = None


class FundingSourceGroupResponse(FundingSourceDateFields):
    def __init__(
        self,
        id: str,
        group_id: str,
        label: str,
        created_date: datetime = None,
        updated_date: datetime = None,
        expiry_date: datetime = None,
        **kwargs,
    ):
        super().__init__(created_date, updated_date, expiry_date)
        self.id = id
        self.group_id = group_id
        self.label = label


class FundingSourcesMixin(ClientProtocol):
    """Mixin implements APIs for funding sources."""

    FUNDING_SOURCES = "fundingsources"

    def funding_source_by_token_endpoint(self, card_token) -> str:
        """Endpoint for a funding source by card token."""
        return self._make_endpoint(self.FUNDING_SOURCES, "bytoken", card_token)

    def funding_source_concession_groups_endpoint(self, funding_source_id) -> str:
        """Endpoint for a funding source's concession groups."""
        return self._make_endpoint(self.FUNDING_SOURCES, funding_source_id, "concession_groups")

    def get_funding_source_by_token(self, card_token) -> FundingSourceResponse:
        """Return a FundingSourceResponse object from the funding source by token endpoint."""
        endpoint = self.funding_source_by_token_endpoint(card_token)
        return self._get(endpoint, FundingSourceResponse)

    def get_funding_source_linked_concession_groups(
        self, funding_source_id: str
    ) -> Generator[FundingSourceGroupResponse, None, None]:
        """Yield FundingSourceGroupResponse objects representing linked concession groups."""
        endpoint = self.funding_source_concession_groups_endpoint(funding_source_id)
        for item in self._get_list(endpoint, per_page=100):
            yield FundingSourceGroupResponse(**item)
