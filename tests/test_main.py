import pytest

from littlepay.main import main, __name__ as MODULE


@pytest.fixture
def mock_commands_info(mock_commands_info):
    return mock_commands_info(MODULE)


def test_main_info(mock_commands_info):
    main(argv=["info"])

    mock_commands_info.assert_called_once()


def test_main_info_default(mock_commands_info):
    main(argv=[])

    mock_commands_info.assert_called_once()
