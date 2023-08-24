import time

from requests import Request, Session

from littlepay import __version__ as version


def _current_time() -> int:
    """Returns the current time as integer seconds since Unix epoch."""
    return int(time.time())


class Client:
    """Represents an API connection to an environment."""

    current_time = staticmethod(_current_time)

    def __init__(
        self,
        env_api_url: str,
        client_id: str,
        client_secret: str,
        audience: str,
        token: dict = None,
        env_api_version: str = "v1",
    ):
        """Initialize a new Client for an API environment. Optionally use an existing access token."""
        self.credentials = dict(
            audience=audience,
            client_id=client_id,
            client_secret=client_secret,
            grant_type="client_credentials",
        )
        self.env_api_url = env_api_url
        self.env_api_version = env_api_version

        self.session = Session()
        self.session.headers.update(
            {"Accept": "application/json", "Content-Type": "application/json", "User-Agent": f"cal-itp/littlepay:{version}"}
        )

        if isinstance(token, dict):
            self._token = token
            self._token_time = Client.current_time()
        else:
            self._token = None
            self._token_time = 0

        token_req = Request(method="POST", url=self.token_endpoint, json=self.credentials)
        self.token_refresh_request = self.session.prepare_request(token_req)

    @property
    def token(self) -> str:
        if not self.token_valid:
            response = self.session.send(self.token_refresh_request)
            self._token = response.json()
            self._token_time = Client.current_time()
        return self._token

    @property
    def token_endpoint(self) -> str:
        """API endpoint to acquire an API access token."""
        return self._version_endpoint("oauth/token")

    @property
    def token_expiry(self) -> int:
        """Get the time in seconds since Unix epoch that this Client's token expires."""
        return self._token_time + self._token.get("expires_in")

    @property
    def token_valid(self) -> bool:
        """True if this Client has a token that is unexpired. False otherwise."""
        return (
            # a token is required
            isinstance(self._token, dict)
            and
            # check that the current time is less than the token's expiry time
            # offset by 1 second, to account for a check right near the expiry time
            Client.current_time() < self.token_expiry - 1
        )

    def _version_endpoint(self, partial_endpoint: str) -> str:
        """Get a complete endpoint with base URL and API version."""
        return f"{self.env_api_url}/api/{self.env_api_version}/{partial_endpoint.lstrip('/')}"
