from dataclasses import dataclass
from typing import Generator, Protocol, TypeVar

from authlib.integrations.requests_client import OAuth2Session


# Generic type parameter, used to represent the result of an API call.
TResponse = TypeVar("TResponse")


@dataclass
class ListResponse:
    """An API response with list and total_count attributes."""

    list: list
    total_count: int


class ClientProtocol(Protocol):
    """Protocol describing key functionality for an API connection."""

    headers: dict
    oauth: OAuth2Session

    def _get(self, endpoint: str, response_cls: TResponse, **kwargs) -> TResponse:
        """Make a GET request to a JSON endpoint.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            endpoint (str): The fully-formed endpoint where the GET request should be made.

            response_cls (TResponse): A dataclass representing the JSON response to the GET.

            Extra kwargs are passed as querystring params.

        Returns (TResponse):
            A TResponse instance of the JSON response.
        """
        pass

    def _get_list(self, endpoint: str) -> Generator[dict, None, None]:
        """Make a GET request to a JSON endpoint returning a ListResponse, yielding items from the resulting list.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            endpoint (str): The fully-formed endpoint where the GET request should be made.

            response_cls (TResponse): A dataclass representing the JSON response to the GET.

        Returns (TResponse):
            A TResponse instance of the JSON response.
        """
        pass

    def _make_endpoint(self, *parts: str) -> str:
        """Create a complete API URL from the endpoint-specific parts.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            *parts tuple[str]: the trailing parts of the endpoint, like ("oauth", "token").

        Returns (str):
            A complete URL for the endpoint.
        """
        pass
