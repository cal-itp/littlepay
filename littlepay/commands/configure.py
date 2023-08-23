from pathlib import Path

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.config import Config


def configure(config_path: str | Path = None, reset: bool = False) -> int:
    """Get or set project configuration.

    Returns:
        A value indicating whether or not the current environment and participant are configured.
    """
    if config_path is None:
        config_path = Config.current_path()
    config = Config(config_path, reset=reset)
    current_config_path = Config.current_path()

    env = config.active_env_name()
    participant = config.active_participant_id()

    print(f"Config: {current_config_path}")
    print(f"Envs: {', '.join(config.envs.keys())}")
    print(f"Participants: {', '.join(config.participants.keys())}")

    if participant == "":
        print(f"Active: {env}, [no participant]")
        return RESULT_FAILURE

    try:
        credentials = config.active_credentials(required=True)
    except ValueError:
        credentials = None

    if credentials is None:
        print(f"Active: {env}, {participant} [missing credentials]")
        return RESULT_FAILURE
    else:
        print(f"Active: {env}, {participant}")
        return RESULT_SUCCESS
