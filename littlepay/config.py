import os
from pathlib import Path
import yaml


CONFIG_DIR = Path(os.environ.get("LP_CONFIG_DIR", "~/.littlepay")).expanduser()
CONFIG_FILE_CURRENT = CONFIG_DIR / ".current"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"

ENV_QA = "qa"
ENV_PROD = "prod"
ENVS = [ENV_QA, ENV_PROD]

DEFAULT_ACTIVE = {"env": ENV_QA, "participant": ""}
DEFAULT_CREDENTIALS = {"client_id": "", "client_secret": "", "audience": ""}
DEFAULT_ENV = {"url": "", "version": "v1"}
DEFAULT_CONFIG = {
    "active": DEFAULT_ACTIVE,
    "envs": {ENV_QA: DEFAULT_ENV, ENV_PROD: DEFAULT_ENV},
    "participants": {"cst": {ENV_QA: DEFAULT_CREDENTIALS, ENV_PROD: DEFAULT_CREDENTIALS}},
}
CONFIG_TYPES = list(DEFAULT_ACTIVE.keys())


def _get_current_path() -> Path:
    """
    Returns (Path):
        The path to the config file currently in-use, or the default.
    """
    CONFIG_FILE_CURRENT.parent.mkdir(parents=True, exist_ok=True)
    if not CONFIG_FILE_CURRENT.exists():
        CONFIG_FILE_CURRENT.touch()
        _update_current_path(DEFAULT_CONFIG_FILE)
    current = CONFIG_FILE_CURRENT.read_text().strip()
    return Path(current)


def _update_current_path(new_path: str | Path):
    """Saves new_path as the path to the current config file."""
    if isinstance(new_path, Path):
        new_path = str(new_path.expanduser().absolute())
    CONFIG_FILE_CURRENT.write_text(new_path)


def _update_current_path(new_path: str | Path):
    """Saves new_path as the path to the current config file."""
    if isinstance(new_path, Path):
        new_path = str(new_path.expanduser().absolute())
    CONFIG_FILE_CURRENT.write_text(new_path)


def _read_config(config_file: Path) -> dict:
    """Reads configuration data from config_file."""
    return yaml.safe_load(config_file.read_text())


def _write_config(config: dict, config_file: Path) -> None:
    """Writes configuration data to config_file."""
    class NoAliasDumper(yaml.SafeDumper):
        """Forces pyyaml to write without aliases.

        See https://github.com/yaml/pyyaml/issues/103.
        """
        def ignore_aliases(self, _):
            return True

    config_file.write_text(yaml.dump(config, Dumper=NoAliasDumper))

class Config:
    """Interface to the configuration backend."""

    current_path = staticmethod(_get_current_path)
    update_path = staticmethod(_update_current_path)
    read = staticmethod(_read_config)
    write = staticmethod(_write_config)

    def __init__(self, config_file_path: str | Path = None, reset: bool = False):
        """Initialize a new Config instance, reading from the given path or a default location.

        Args:
            config_file_path (str|Path): Path to a readable config file. If None, the default is used.

            reset (bool): True to reset the configuration to the default.
        """
        if config_file_path is None or config_file_path == "":
            config_file_path = Config.current_path()
        if isinstance(config_file_path, str):
            config_file_path = Path(config_file_path)
        if not config_file_path.exists() or reset:
            print(f"Creating config file: {config_file_path.resolve()}")
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            Config.write(DEFAULT_CONFIG, config_file_path)

        Config.update_path(config_file_path)

        data = Config.read(config_file_path)
        for key, value in data.items():
            setattr(self, key, value)

    def active_credentials(self, required: bool = False) -> dict:
        """Get credentials from the active participant's environment config.

        Args:
            required (bool): If True, raise a ValueError for missing credentials.
        """
        participant = self.active_participant()
        for key in [k for k in DEFAULT_CREDENTIALS.keys() if required and k not in participant]:
            raise ValueError(f"Participant missing required credential: {key}")
        return {key: value for key, value in participant.items() if key in DEFAULT_CREDENTIALS.keys()}

    def active_env(self) -> dict:
        """
        Returns (dict):
            Configuration data for the active environment.
        """
        return self.envs[self.active_env_name()]

    def active_env_name(self, new_env: str = None) -> str:
        """Get or set the active environment by name. By default, the QA environment.

        Args:
            new_env (str): The new environment name to activate. Must exist.

        Returns (str):
            The name of the active environment.
        """
        if new_env is not None:
            if new_env not in self.envs:
                raise ValueError(f"Unsupported env: {new_env}, must be one of: {', '.join(self.envs.keys())}")

            self.active["env"] = new_env
            Config.write(self.__dict__, Config.current_path())

        return self.active.get("env", ENV_QA)

    def active_participant(self) -> dict:
        """
        Returns (dict):
            Configuration data for the active participant.
        """
        return self.participants[self.active_participant_id()][self.active_env_name()]

    def active_participant_id(self, new_participant: str = None) -> str:
        """Get or set the active participant by participant_id.

        Args:
            new_participant (str): The new participant_id to activate. Must exist.

        Returns (str):
            The participant_id of the active participant.
        """
        if new_participant is not None:
            if new_participant not in self.participants:
                raise ValueError(
                    f"Unsupported participant: {new_participant}, must be one of: {', '.join(self.participants.keys())}"
                )

            self.active["participant"] = new_participant
            Config.write(self.__dict__, Config.current_path())

        # ensure active is always a str, even if missing (e.g. None)
        return self.active.get("participant", "") or ""
