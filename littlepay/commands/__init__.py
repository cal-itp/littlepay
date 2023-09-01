from littlepay.config import ENV_PROD, Config


RESULT_SUCCESS = 0
RESULT_FAILURE = 1


def print_active_message(config: Config, message: str, postfix: str = None):
    """Print a message including information about the active configuration."""
    alert = "⚠️  " if config.active_env_name == ENV_PROD else ""
    line = f"{message}: {alert}{config.active_env_name}, {config.active_participant_id}{' ' + postfix if postfix else ''}"
    print(line.strip())
