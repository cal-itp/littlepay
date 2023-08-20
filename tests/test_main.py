import pytest

from littlepay.commands import RESULT_SUCCESS
from littlepay.config import CONFIG_TYPES
from littlepay.main import main, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


@pytest.fixture
def mock_commands_switch(mock_commands_switch):
    return mock_commands_switch(MODULE)


def test_main_config(mock_commands_config):
    result = main(argv=["config"])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once()


def test_main_default(mock_commands_config):
    result = main(argv=[])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once()


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
