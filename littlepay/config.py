import os
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("LP_CONFIG_DIR", "~/.littlepay")).expanduser()
CONFIG_FILE_CURRENT = CONFIG_DIR / ".current"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"


def get_config_path() -> Path:
    """Gets a pathlib.Path of the config file currently in-use, or the default if None."""
    CONFIG_FILE_CURRENT.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE_CURRENT.touch()
    current = CONFIG_FILE_CURRENT.read_text().strip()
    return Path(current or DEFAULT_CONFIG_FILE)
