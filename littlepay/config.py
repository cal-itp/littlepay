import os
from pathlib import Path


CONFIG_DIR = Path(os.environ.get("LP_CONFIG_DIR", "~/.littlepay")).expanduser()
CONFIG_FILE_CURRENT = CONFIG_DIR / ".current"
DEFAULT_CONFIG_FILE = CONFIG_DIR / "config.yaml"


def get_config_path() -> Path:
    """Gets a pathlib.Path of the config file currently in-use, or the default if None."""
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
