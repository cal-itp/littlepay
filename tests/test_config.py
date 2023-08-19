from pathlib import Path

from littlepay.config import get_config_path


def test_get_config_path_default(custom_config_file: Path):
    result = get_config_path()

    assert isinstance(result, Path)
    assert result.absolute() == custom_config_file.absolute()


def test_get_config_path_current(custom_current_file: Path):
    expected = "."
    custom_current_file.write_text(expected)

    result = get_config_path()

    assert result == Path(expected)
