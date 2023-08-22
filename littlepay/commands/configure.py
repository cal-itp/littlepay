from pathlib import Path

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.config import active_env, active_participant, all_envs, all_participants, get_config, get_config_path


def configure(config_path: str | Path = None, reset: bool = False) -> int:
    """Get or set project configuration.

    Returns:
        A value indicating whether or not the current environment and participant are configured.
    """
    if config_path is None:
        config_path = get_config_path()
    config = get_config(config_file_path=config_path, reset=reset)
    current_config_path = get_config_path()

    env, _ = active_env(config)
    participant, participant_config = active_participant(config)

    print(f"Config: {current_config_path}")
    print(f"Envs: {', '.join(all_envs().keys())}")
    print(f"Participants: {', '.join(all_participants().keys())}")

    if participant == "":
        print(f"Active: {env}, [no participant]")
        return RESULT_FAILURE

    participant_env = participant_config.get(env, {})
    participant_auth = (
        participant_env.get("client_id"),
        participant_env.get("client_secret"),
        participant_env.get("audience"),
    )

    if not all(participant_auth):
        print(f"Active: {env}, {participant} [missing auth]")
        return RESULT_FAILURE
    else:
        print(f"Active: {env}, {participant}")
        return RESULT_SUCCESS
