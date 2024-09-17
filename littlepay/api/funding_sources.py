from dataclasses import dataclass
from datetime import datetime
from typing import Generator, List, Optional

from littlepay.api import ClientProtocol

from . import from_kwargs


@dataclass
class FundingSourceResponse:
    id: str
    card_first_digits: str
    card_last_digits: str
    card_expiry_month: str
    card_expiry_year: str
    card_scheme: str
    form_factor: str
    participant_id: str
    is_fpan: bool
    related_funding_sources: List[dict]
    created_date: datetime | None = None
    card_category: Optional[str] = None
    issuer_country_code: Optional[str] = None
    issuer_country_numeric_code: Optional[str] = None
    replacement_funding_source: Optional[str] = None
    token: Optional[str] = None
    token_key_id: Optional[str] = None
    icc_hash: Optional[str] = None

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)

    def __post_init__(self):
        """Parses any date parameters into Python datetime objects.

        For @dataclasses with a generated __init__ function, this function is called automatically.

        Includes a workaround for Python 3.10 where datetime.fromisoformat() can only parse the format output
        by datetime.isoformat(), i.e. without a trailing 'Z' offset character and with UTC offset expressed
        as +/-HH:mm

        https://docs.python.org/3.11/library/datetime.html#datetime.datetime.fromisoformat
        """
        if self.created_date:
            self.created_date = datetime.fromisoformat(self.created_date.replace("Z", "+00:00", 1))
        else:
            self.created_date = None


@dataclass
class FundingSourceDateFields:
    """Implements parsing of datetime strings to Python datetime objects for funding source fields."""

    created_date: datetime | None = None
    updated_date: datetime | None = None
    expiry_date: datetime | None = None

    def __post_init__(self):
        """Parses any date parameters into Python datetime objects.

        For @dataclasses with a generated __init__ function, this function is called automatically.

        Includes a workaround for Python 3.10 where datetime.fromisoformat() can only parse the format output
        by datetime.isoformat(), i.e. without a trailing 'Z' offset character and with UTC offset expressed
        as +/-HH:mm

        https://docs.python.org/3.11/library/datetime.html#datetime.datetime.fromisoformat
        """
        if self.created_date:
            self.created_date = datetime.fromisoformat(self.created_date.replace("Z", "+00:00", 1))
        else:
            self.created_date = None
        if self.updated_date:
            self.updated_date = datetime.fromisoformat(self.updated_date.replace("Z", "+00:00", 1))
        else:
            self.updated_date = None
        if self.expiry_date:
            self.expiry_date = datetime.fromisoformat(self.expiry_date.replace("Z", "+00:00", 1))
        else:
            self.expiry_date = None


@dataclass(kw_only=True)
class FundingSourceGroupResponse(FundingSourceDateFields):
    id: str
    group_id: str
    label: str

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)


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
