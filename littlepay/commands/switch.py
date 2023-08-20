from littlepay.commands.configure import configure
from littlepay.config import CONFIG_TYPES, Config


def switch(switch_type: str, switch_arg: str) -> int:
    if switch_type not in CONFIG_TYPES:
        raise ValueError(f"Unsupported type: {switch_type}, must be one of: {', '.join(CONFIG_TYPES)}")

    config = Config()

    if switch_type == "env":
        config.active_env_name = switch_arg
    elif switch_type == "participant":
        config.active_participant_id = switch_arg

    return configure()
