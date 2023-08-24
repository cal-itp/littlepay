from authlib.integrations.requests_client import OAuth2Session


class Client:
    """Represents an API connection to an environment."""

    def __init__(self, env_api_url: str, client_id: str, client_secret: str, audience: str, token: str = None):
        """Initialize a new Client to connect to an API environment. Optionally use an existing access token."""
        self.env_api_url = env_api_url
        self.client_id = client_id
        self.client_secret = client_secret
        self.audience = audience
        self.session = OAuth2Session(
            token_endpoint=self.token_endpoint,
            client_id=self.client_id,
            client_secret=self.client_secret,
            audience=self.audience,
            grant_type="client_credentials",
            token=token,
        )

    @property
    def token_endpoint(self) -> str:
        """API endpoint to acquire an API access token."""
        return f"{self.env_api_url}/oauth/token"

    @property
    def token(self) -> str:
        raise NotImplementedError()
