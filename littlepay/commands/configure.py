from pathlib import Path

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.config import ENV_PROD, Config


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

    if config.active_participant_id == "":
        print(f"Active: {config.active_env_name}, [no participant]")
        return RESULT_FAILURE

    try:
        credentials = config.active_credentials
    except ValueError:
        credentials = None

    if credentials is None or not all(credentials.values()):
        print(f"Active: {config.active_env_name}, {config.active_participant_id} [missing credentials]".strip())
        return RESULT_FAILURE
    else:
        alert = "⚠️  " if config.active_env_name == ENV_PROD else ""
        print(f"Active: {alert}{config.active_env_name}, {config.active_participant_id}".strip())

        return RESULT_SUCCESS
