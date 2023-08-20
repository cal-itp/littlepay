from littlepay.commands.configure import configure
from littlepay.config import CONFIG_ENV, CONFIG_PARTICIPANT, CONFIG_TYPES, active_env, active_participant


def switch(switch_type: str, switch_arg: str) -> int:
    if switch_type not in CONFIG_TYPES:
        raise ValueError(f"Unsupported type: {switch_type}, must be one of: {', '.join(CONFIG_TYPES)}")

    if switch_type == CONFIG_ENV:
        active_env(new_env=switch_arg)
    elif switch_type == CONFIG_PARTICIPANT:
        active_participant(new_participant=switch_arg)

    return configure()
