from typing import Protocol

from authlib.integrations.requests_client import OAuth2Session


class ClientProtocol(Protocol):
    """Protocol describing key functionality for an API connection."""

    headers: dict
    oauth: OAuth2Session

    def _make_endpoint(self, *parts: str) -> str:
        """Create a complete API URL from the endpoint-specific parts.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            *parts tuple[str]: the trailing parts of the endpoint, like ("oauth", "token").

        Returns (str):
            A complete URL for the endpoint.
        """
        pass
