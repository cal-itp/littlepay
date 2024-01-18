from dataclasses import dataclass
from typing import List

from littlepay.api import ClientProtocol


@dataclass
class FundingSourceResponse:
    id: str
    card_first_digits: str
    card_last_digits: str
    card_expiry_month: str
    card_expiry_year: str
    card_scheme: str
    # card_category: str
    form_factor: str
    participant_id: str
    is_fpan: bool
    related_funding_sources: List[dict]
    # issuer_country_code: str
    # issuer_country_numeric_code: str
    # replacement_funding_source: str
    # token: str
    # token_key_id: str
    # icc_hash: str


class FundingSourcesMixin(ClientProtocol):
    """Mixin implements APIs for funding sources."""

    FUNDING_SOURCES = "fundingsources"

    def funding_source_by_token_endpoint(self, card_token) -> str:
        return self._make_endpoint(self.FUNDING_SOURCES, "bytoken", card_token)

    def get_funding_source_by_token(self, card_token) -> FundingSourceResponse:
        endpoint = self.funding_source_by_token_endpoint(card_token)
        return self._get(endpoint, FundingSourceResponse)
