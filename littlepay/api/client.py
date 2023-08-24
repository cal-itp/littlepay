import json

from authlib.common.urls import url_decode
from authlib.integrations.requests_client import OAuth2Session
from authlib.oauth2.rfc6749 import OAuth2Token

from littlepay import __version__
from littlepay.config import Config


def _client_from_active_config(config: Config):
    """Create an API client for the active config targets.

    This function should not be called directly, use the static method Client.from_active_config(Config) instead.

    Args:
        config (Config): The Config instance from which to read initialization values.
    """
    return Client(
        base_url=config.active_env["url"],
        version=config.active_env.get("version", "v1"),
        token=config.active_token,
        **config.active_credentials,
    )


def _json_post_credentials(client, method, uri, headers, body) -> tuple:
    """Custom authentication converts x-www-form-urlencoded body (Authlib default) into JSON (Littlepay requirement).

    This function should not be called directly, it is used by Client.oauth.

    See https://docs.authlib.org/en/latest/client/oauth2.html#client-authentication
    """
    data = dict(url_decode(body))
    json_data = json.dumps(data)
    headers["Content-Length"] = len(json_data)

    return uri, headers, json_data


class Client:
    """Represents an API connection to an environment."""

    from_active_config = staticmethod(_client_from_active_config)

    def __init__(
        self, base_url: str, client_id: str, client_secret: str, audience: str, token: dict = None, version: str = "v1"
    ):
        """Initialize a new Client to connect to an API environment.

        Args:
            base_url (str): Environment-specific base URL for all API endpoints.

            client_id (str): Environment and participant specific value provided by Littlepay.

            client_secret (str): Environment and participant specific value provided by Littlepay.

            audience (str): Environment and participant specific value provided by Littlepay.

            token (dict): Access token acquired previously, granting access to protected API resources.

            version (str): The API version to target.
        """
        self.credentials = dict(
            audience=audience, client_id=client_id, client_secret=client_secret, grant_type="client_credentials"
        )
        self.base_url = base_url
        self.version = version

        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": f"cal-itp/littlepay:{__version__}",
        }

        if token is None or OAuth2Token.from_dict(token).is_expired():
            token = None

        self.oauth = OAuth2Session(
            token_endpoint=self.token_endpoint, token_endpoint_auth_method=_json_post_credentials, token=token
        )

    @property
    def token_endpoint(self) -> str:
        """Endpoint to acquire an API access token."""
        return self._make_endpoint("oauth", "token")

    @property
    def token(self) -> OAuth2Token:
        """This client's API access token."""
        if self.oauth.token is None or self.oauth.token.is_expired():
            self.oauth.token = self.oauth.fetch_token(headers=self.headers, **self.credentials)
        return self.oauth.token

    def _make_endpoint(self, *parts: str) -> str:
        parts = (p.strip("/") for p in parts)
        return "/".join((self.base_url, "api", self.version, *parts))
