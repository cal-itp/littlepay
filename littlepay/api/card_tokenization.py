from authlib.oauth2.rfc6749 import OAuth2Token

from littlepay.api import ClientProtocol


class CardTokenizationMixin(ClientProtocol):
    """Mixin implements APIs for card tokenization."""

    def card_tokenization_request_access_endpoint(self) -> str:
        """Endpoint to acquire a card tokenization access token."""
        return self._make_endpoint("cardtokenisation", "requestaccess")

    def request_card_tokenization_access(self) -> OAuth2Token:
        """Request an access token for card tokenization."""
        endpoint = self.card_tokenization_request_access_endpoint()
        request_body = {"request_access": "CARD_TOKENISATION"}

        response_dict = self._post(endpoint, request_body)
        return OAuth2Token.from_dict(response_dict)
