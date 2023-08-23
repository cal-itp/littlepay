from pathlib import Path

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.config import ENV_PROD, Config


def configure(config_path: str | Path = None, reset: bool = False) -> int:
    """Get or set project configuration.

    Returns:
        A value indicating whether or not the current environment and participant are configured.
    """
    if config_path is None:
        config_path = Config.current_path()
    config = Config(config_path, reset=reset)
    current_config_path = Config.current_path()

    env_name = config.active_env_name()
    participant_id = config.active_participant_id()

    print(f"Config: {current_config_path}")
    print(f"Envs: {', '.join(config.envs.keys())}")
    print(f"Participants: {', '.join(config.participants.keys())}")

    if participant_id == "":
        print(f"Active: {env_name}, [no participant]")
        return RESULT_FAILURE

    try:
        credentials = config.active_credentials(required=True)
    except ValueError:
        credentials = None

    if credentials is None or not all(credentials.values()):
        print(f"Active: {env_name}, {participant_id} [missing credentials]".strip())
        return RESULT_FAILURE
    else:
        alert = "⚠️  " if env_name == ENV_PROD else ""
        print(f"Active: {alert}{env_name}, {participant_id}".strip())

        return RESULT_SUCCESS
