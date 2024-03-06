import datetime
from pathlib import Path

from littlepay.api.client import Client
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS, print_active_message
from littlepay.config import Config


def configure(config_path: str | Path = None) -> int:
    """Get or set project configuration.

    Returns:
        A value indicating whether or not the current environment and participant are configured.
    """
    if config_path is None:
        config_path = Config.current_path()

    config = Config(config_path)
    current_config_path = Config.current_path()

    print(f"Config: {current_config_path}")
    print(f"Envs: {', '.join(config.envs.keys())}")
    print(f"Participants: {', '.join(config.participants.keys())}")

    if config.active_env_name == "" or config.active_participant_id == "":
        env = config.active_env_name if config.active_env_name else "[no env]"
        participant = config.active_participant_id if config.active_participant_id else "[no participant]"
        print(f"❓ Active: {env}, {participant}")
        return RESULT_SUCCESS

    try:
        credentials = config.active_credentials
    except ValueError:
        credentials = None

    if credentials is None or not all(credentials.values()):
        print_active_message(config, "❌ Active", "[missing credentials]")
        return RESULT_FAILURE

    # save the active token for reuse in later commands
    config.active_token = Client.from_active_config(config).token

    if config.active_token is None or config.active_token == {}:
        print_active_message(config, "❌ Active", "[misconfigured credentials]")
        return RESULT_FAILURE
    else:
        print_active_message(config, "Active")
        if "expires_at" in config.active_token:
            expiry = datetime.datetime.fromtimestamp(config.active_token["expires_at"])
            print(f"✅ Token expires: {expiry.isoformat()} UTC")
        return RESULT_SUCCESS
