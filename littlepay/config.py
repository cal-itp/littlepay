import os
from pathlib import Path
import yaml


CONFIG_DIR = Path(os.environ.get("LP_CONFIG_DIR", "~/.littlepay")).expanduser()
CONFIG_FILE_CURRENT = CONFIG_DIR / ".current"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"

ENV_QA = "qa"
ENV_PROD = "prod"
ENVS = [ENV_QA, ENV_PROD]

CONFIG_ACTIVE = "active"
CONFIG_ENV = "env"
CONFIG_ENVS = f"{CONFIG_ENV}s"
CONFIG_PARTICIPANT = "participant"
CONFIG_PARTICIPANTS = f"{CONFIG_PARTICIPANT}s"
CONFIG_TYPES = [CONFIG_ENV, CONFIG_PARTICIPANT]

DEFAULT_CONFIG = {
    CONFIG_ACTIVE: {CONFIG_ENV: ENV_QA, CONFIG_PARTICIPANT: ""},
    f"{CONFIG_ENVS}": {ENV_QA: {"url": ""}, ENV_PROD: {"url": ""}},
    f"{CONFIG_PARTICIPANTS}": {"cst": {"client_id": "", "client_secret": "", "audience": ""}},
}


def get_config_path() -> Path:
    """Gets a pathlib.Path of the config file currently in-use, or the default if None."""
    CONFIG_FILE_CURRENT.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE_CURRENT.touch()
    current = CONFIG_FILE_CURRENT.read_text().strip()
    return Path(current or DEFAULT_CONFIG_FILE)


def _read_config(config_file_path: Path = None) -> dict:
    if config_file_path is None:
        config_file_path = get_config_path()
    return yaml.safe_load(config_file_path.read_text())


def _write_config(config: dict, config_file_path: Path = None) -> None:
    if config_file_path is None:
        config_file_path = get_config_path()
    config_file_path.write_text(yaml.dump(config))


def get_config(config_file_path: str | Path = None, reset: bool = False) -> dict:
    """If config_file_path does not exist, creates it with a default configuration.

    Returns a dict representation of the config file.
    """
    if config_file_path is None or config_file_path == "":
        config_file_path = get_config_path()
    if isinstance(config_file_path, str):
        config_file_path = Path(config_file_path)
    if not config_file_path.exists() or reset:
        print(f"Creating config file: {config_file_path.resolve()}")
        config_file_path.parent.mkdir(parents=True, exist_ok=True)
        _write_config(DEFAULT_CONFIG, config_file_path)

    CONFIG_FILE_CURRENT.write_text(str(config_file_path.resolve()))
    return _read_config(config_file_path)
