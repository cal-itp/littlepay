from dataclasses import dataclass
from typing import List, Optional

from littlepay.api import ClientProtocol


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
    card_category: Optional[str] = None
    issuer_country_code: Optional[str] = None
    issuer_country_numeric_code: Optional[str] = None
    replacement_funding_source: Optional[str] = None
    token: Optional[str] = None
    token_key_id: Optional[str] = None
    icc_hash: Optional[str] = None


class FundingSourcesMixin(ClientProtocol):
    """Mixin implements APIs for funding sources."""

    FUNDING_SOURCES = "fundingsources"

    def funding_source_by_token_endpoint(self, card_token) -> str:
        """Endpoint for a funding source by card token."""
        return self._make_endpoint(self.FUNDING_SOURCES, "bytoken", card_token)

    def get_funding_source_by_token(self, card_token) -> FundingSourceResponse:
        """Return a FundingSourceResponse object from the funding source by token endpoint."""
        endpoint = self.funding_source_by_token_endpoint(card_token)
        return self._get(endpoint, FundingSourceResponse)
