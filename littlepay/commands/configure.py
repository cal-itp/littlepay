from pathlib import Path

from littlepay.commands import RESULT_SUCCESS
from littlepay.config import active_env, active_participant, all_envs, all_participants, get_config, get_config_path


def configure(config_path: str | Path = None, reset: bool = False) -> int:
    """Get or set project configuration.

    Returns:
        A value indicating if the operation succeeded or failed.
    """
    if config_path is None:
        config_path = get_config_path()
    config = get_config(config_file_path=config_path, reset=reset)
    current_config_path = get_config_path()

    env, _ = active_env(config)
    participant, _ = active_participant(config)

    print(f"Config: {current_config_path}")
    print(f"Envs: {', '.join(all_envs().keys())}")
    print(f"Participants: {', '.join(all_participants().keys())}")

    if participant != "":
        print(f"Active: {env}, {participant}")
    else:
        print(f"Active: {env} [no participant]")

    return RESULT_SUCCESS
