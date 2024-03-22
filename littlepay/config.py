import os
from pathlib import Path
import yaml


CONFIG_DIR = Path(os.environ.get("LP_CONFIG_DIR", "~/.littlepay")).expanduser()
CONFIG_FILE_CURRENT = CONFIG_DIR / ".current"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"

ENV_QA = "qa"
ENV_PROD = "prod"

DEFAULT_ACTIVE = {"env": ENV_QA, "participant": ""}
DEFAULT_CREDENTIALS = {"client_id": "", "client_secret": "", "audience": ""}
DEFAULT_ENV = {"url": "", "version": "v1"}
DEFAULT_CONFIG = {
    "active": DEFAULT_ACTIVE,
    "envs": {ENV_QA: DEFAULT_ENV, ENV_PROD: DEFAULT_ENV},
    "participants": {"cst": {ENV_QA: DEFAULT_CREDENTIALS, ENV_PROD: DEFAULT_CREDENTIALS}},
}
CONFIG_TYPES = list(DEFAULT_ACTIVE.keys())


def _ensure_current_exists() -> bool:
    """
    Creates the CONFIG_FILE_CURRENT file if it doesn't already exist.

    Returns (bool):
        A flag indicating if the file existed or not.
    """
    exists = CONFIG_FILE_CURRENT.exists()
    if not exists:
        CONFIG_FILE_CURRENT.parent.mkdir(parents=True, exist_ok=True)
        CONFIG_FILE_CURRENT.touch()
    return exists


def _get_current_path() -> Path:
    """
    Returns (Path):
        The path to the config file currently in-use, or the default.
    """
    if not _ensure_current_exists():
        _update_current_path(DEFAULT_CONFIG_FILE)
    current = CONFIG_FILE_CURRENT.read_text().strip()
    return Path(current)


def _update_current_path(new_path: str | Path):
    """Saves new_path as the path to the current config file."""
    if isinstance(new_path, Path):
        new_path = str(new_path.expanduser().absolute())
    _ensure_current_exists()
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

    def __init__(self, config_file_path: str | Path = None):
        """Initialize a new Config instance, reading from the given path or a default location.

        Args:
            config_file_path (str|Path): Path to a readable config file. If None, the default is used.
        """
        if config_file_path is None or config_file_path == "":
            config_file_path = Config.current_path()
        if isinstance(config_file_path, str):
            config_file_path = Path(config_file_path)
        if not config_file_path.exists():
            print(f"Creating config file: {config_file_path.resolve()}")
            config_file_path.parent.mkdir(parents=True, exist_ok=True)
            Config.write(DEFAULT_CONFIG, config_file_path)

        Config.update_path(config_file_path)

        data = Config.read(config_file_path)
        for key, value in data.items():
            setattr(self, key, value)

    @property
    def active_env(self) -> dict:
        """
        Returns (dict):
            Configuration data for the active environment.
        """
        active_env_name = self.active_env_name
        if not active_env_name:
            raise ValueError("Missing active env")
        return self.envs[active_env_name]

    @property
    def active_participant(self) -> dict:
        """
        Returns (dict):
            Configuration data for the active participant.
        """
        active_participant = self.participants.get(self.active_participant_id)
        if active_participant is None:
            raise ValueError("Missing an active participant")
        return active_participant[self.active_env_name]

    @property
    def active_credentials(self) -> dict:
        """Get credentials from the active participant's environment config."""
        credentials = {key: value for key, value in self.active_participant.items() if key in DEFAULT_CREDENTIALS.keys()}
        if credentials.keys() != DEFAULT_CREDENTIALS.keys():
            raise ValueError("Missing credentials")
        return credentials

    @property
    def active_env_name(self) -> str:
        """The active environment's name."""
        return self.active.get("env", "")

    @active_env_name.setter
    def active_env_name(self, value: str):
        if value not in self.envs:
            raise ValueError(f"Unsupported env: {value}, must be one of: {', '.join(self.envs.keys())}")

        self.active["env"] = value
        Config.write(self.__dict__, Config.current_path())

    @property
    def active_participant_id(self) -> str:
        """The active participant's participant_id."""
        # ensure active is always a str, even if missing (e.g. None)
        return self.active.get("participant", "") or ""

    @active_participant_id.setter
    def active_participant_id(self, value: str):
        if value not in self.participants:
            raise ValueError(f"Unsupported participant: {value}, must be one of: {', '.join(self.participants.keys())}")

        self.active["participant"] = value
        Config.write(self.__dict__, Config.current_path())

    @property
    def active_token(self) -> dict:
        """The active participant's API access token."""
        return self.active_participant.get("token", None)

    @active_token.setter
    def active_token(self, value: dict):
        self.active_participant["token"] = dict(value)
        Config.write(self.__dict__, Config.current_path())
