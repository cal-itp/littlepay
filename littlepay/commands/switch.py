from littlepay.commands.configure import configure
from littlepay.config import Config


def switch(env: str = None, participant: str = None) -> int:
    if not (participant or env):
        raise ValueError("Unsupported type: provide at least one of participant or env.")

    config = Config()

    if env:
        config.active_env_name = env
    if participant:
        config.active_participant_id = participant

    return configure()
