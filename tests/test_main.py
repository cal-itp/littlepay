import pytest

from littlepay.commands import RESULT_SUCCESS
from littlepay.main import main, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


def test_main_config(mock_commands_config):
    result = main(argv=["config"])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once()


def test_main_default(mock_commands_config):
    result = main(argv=[])

    assert result == RESULT_SUCCESS
    mock_commands_config.assert_called_once()


def test_main_unrecognized(capfd):
    with pytest.raises(SystemExit) as err:
        main(argv=["unrecognized"])

    capture = capfd.readouterr()
    assert err.value.code != RESULT_SUCCESS
    assert "usage: littlepay" in capture.err
