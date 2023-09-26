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

    def _delete(self, endpoint: str) -> bool:
        """Make a DELETE request to an endpoint.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            endpoint (str): The fully-formed endpoint where the DELETE request should be made.

        Returns (bool):
            A value indicating that the delete operation succeeded.
        """
        pass

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

    def _get_list(self, endpoint: str, **kwargs: dict) -> Generator[dict, None, None]:
        """Make a GET request to a JSON endpoint returning a ListResponse, yielding items from the resulting list.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            endpoint (str): The fully-formed endpoint where the GET request should be made.

            Extra kwargs are passed as querystring params.

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

    def _post(self, endpoint: str, data: dict, response_cls: TResponse = dict, **kwargs) -> TResponse:
        """Make a POST request to a JSON endpoint.

        Args:
            self (ClientProtocol): The current ClientProtocol reference.

            endpoint (str): The fully-formed endpoint where the POST request should be made.

            data (dict): Data to send as JSON in the POST body.

            response_cls (TResponse): A dataclass representing the JSON response to the POST. By default, simply returns a
            boolean indicating success.

            Extra kwargs are passed to requests.post(...)

        Returns (TResponse):
            A TResponse instance of the JSON response.
        """
        pass
