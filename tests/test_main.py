from pathlib import Path
import pytest

from littlepay.commands import RESULT_SUCCESS
from littlepay.config import CONFIG_TYPES, Config
from littlepay.main import main, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


@pytest.fixture
def mock_commands_groups(mock_commands_groups):
    return mock_commands_groups(MODULE)


@pytest.fixture
def mock_commands_switch(mock_commands_switch):
    return mock_commands_switch(MODULE)


def test_main_default(mock_commands_config):
    result = main(argv=[])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with(Config().current_path())


@pytest.mark.parametrize("config_flag", ["-c", "--config"])
def test_main_config_flag(custom_config_file: Path, mock_commands_config, config_flag):
    new_config = custom_config_file.parent / "new_config.yaml"
    assert not new_config.exists()

    new_config_path = str(new_config.absolute())

    result = main(argv=[config_flag, new_config_path])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with(new_config_path)


def test_main_config(mock_commands_config):
    result = main(argv=["config"])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with(Config().current_path())


def test_main_config_config_path(custom_config_file: Path, mock_commands_config):
    new_config = custom_config_file.parent / "new_config.yaml"
    assert not new_config.exists()

    new_config_path = str(new_config.absolute())
    result = main(argv=["config", new_config_path])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once_with(new_config_path)


def test_main_groups(mock_commands_groups):
    result = main(argv=["groups"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()


@pytest.mark.parametrize("filter_flag", ["-f", "--filter"])
def test_main_groups_filter(mock_commands_groups, filter_flag):
    result = main(argv=["groups", filter_flag, "term"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    assert "term" in mock_commands_groups.call_args.args


@pytest.mark.parametrize("switch_type", CONFIG_TYPES)
def test_main_switch_recognized_type(mock_commands_switch, switch_type):
    result = main(argv=["switch", switch_type, "new_value"])

    assert result == RESULT_SUCCESS
    mock_commands_switch.assert_called_once_with(switch_type, "new_value")


def test_main_switch_missing_value(mock_commands_switch):
    with pytest.raises(SystemExit):
        main(argv=["switch", "env"])

    assert mock_commands_switch.call_count == 0


def test_main_switch_unrecognized_type(mock_commands_switch):
    with pytest.raises(SystemExit):
        main(argv=["switch", "unrecognized", "new_value"])

    assert mock_commands_switch.call_count == 0


def test_main_unrecognized(capfd):
    with pytest.raises(SystemExit) as err:
        main(argv=["unrecognized"])

    capture = capfd.readouterr()
    assert err.value.code != RESULT_SUCCESS
    assert "usage: littlepay" in capture.err
