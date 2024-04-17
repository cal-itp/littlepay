from argparse import Namespace
from pathlib import Path
import re

import pytest

from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.config import CONFIG_TYPES, Config
import littlepay.main
from littlepay.main import main, __name__ as MODULE


@pytest.fixture
def mock_commands_config(mock_commands_config):
    return mock_commands_config(MODULE)


@pytest.fixture
def mock_commands_groups(mock_commands_groups):
    return mock_commands_groups(MODULE)


@pytest.fixture
def mock_commands_products(mock_commands_products):
    return mock_commands_products(MODULE)


@pytest.fixture
def mock_commands_switch(mock_commands_switch):
    return mock_commands_switch(MODULE)


def test_main_default(capfd, mock_commands_config):
    result = main(argv=[])
    capture = capfd.readouterr()

    assert result == RESULT_FAILURE
    assert "usage: littlepay" in capture.out
    mock_commands_config.assert_not_called()


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
    call_args = mock_commands_groups.call_args.args[0]
    assert isinstance(call_args, Namespace)
    assert call_args.command == "groups"


def test_main_groups_csv(mock_commands_groups):
    result = main(argv=["groups", "--csv"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert isinstance(call_args, Namespace)
    assert call_args.command == "groups"
    assert call_args.csv is True


@pytest.mark.parametrize("filter_flag", ["-f", "--filter"])
def test_main_groups_filter(mock_commands_groups, filter_flag):
    result = main(argv=["groups", filter_flag, "term"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_terms == ["term"]


@pytest.mark.parametrize("filter_flag", ["-f", "--filter"])
def test_main_groups_filter_multiple(mock_commands_groups, filter_flag):
    result = main(argv=["groups", filter_flag, "term1", filter_flag, "term2"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_terms == ["term1", "term2"]


def test_main_groups_create(mock_commands_groups):
    result = main(argv=["groups", "create", "label"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "create"
    assert call_args.group_label == "label"


def test_main_groups_funding_sources(mock_commands_groups):
    result = main(argv=["groups", "funding_sources"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "funding_sources"


def test_main_groups_link(mock_commands_groups):
    result = main(argv=["groups", "link", "1234"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "link"
    assert call_args.product_id == "1234"


def test_main_groups_migrate(mock_commands_groups):
    result = main(argv=["groups", "migrate"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "migrate"


def test_main_groups_migrate_force(mock_commands_groups):
    result = main(argv=["groups", "migrate", "--force"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "migrate"
    assert call_args.force is True


def test_main_groups_products(mock_commands_groups):
    result = main(argv=["groups", "products"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "products"


def test_main_groups_products_csv(mock_commands_groups):
    result = main(argv=["groups", "products", "--csv"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "products"
    assert call_args.csv is True


def test_main_groups_remove(mock_commands_groups):
    result = main(argv=["groups", "remove", "1234"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "remove"
    assert call_args.group_id == "1234"


@pytest.mark.parametrize("argv", [["groups", "remove", "--force", "1234"], ["groups", "remove", "1234", "--force"]])
def test_main_groups_remove_force(mock_commands_groups, argv):
    result = main(argv=argv)

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "remove"
    assert call_args.group_id == "1234"
    assert call_args.force is True


def test_main_groups_unlink(mock_commands_groups):
    result = main(argv=["groups", "unlink", "1234"])

    assert result == RESULT_SUCCESS
    mock_commands_groups.assert_called_once()
    call_args = mock_commands_groups.call_args.args[0]
    assert call_args.group_command == "unlink"
    assert call_args.product_id == "1234"


def test_main_products(mock_commands_products):
    result = main(argv=["products"])

    assert result == RESULT_SUCCESS
    mock_commands_products.assert_called_once()
    call_args = mock_commands_products.call_args.args[0]
    assert isinstance(call_args, Namespace)
    assert call_args.command == "products"


def test_main_products_csv(mock_commands_products):
    result = main(argv=["products", "--csv"])

    assert result == RESULT_SUCCESS
    mock_commands_products.assert_called_once()
    call_args = mock_commands_products.call_args.args[0]
    assert isinstance(call_args, Namespace)
    assert call_args.command == "products"
    assert call_args.csv is True


@pytest.mark.parametrize("filter_flag", ["-f", "--filter"])
def test_main_products_filter(mock_commands_products, filter_flag):
    result = main(argv=["products", filter_flag, "term"])

    assert result == RESULT_SUCCESS
    mock_commands_products.assert_called_once()
    call_args = mock_commands_products.call_args.args[0]
    assert call_args.product_terms == ["term"]


@pytest.mark.parametrize("filter_flag", ["-f", "--filter"])
def test_main_products_filter_multiple(mock_commands_products, filter_flag):
    result = main(argv=["products", filter_flag, "term1", filter_flag, "term2"])

    assert result == RESULT_SUCCESS
    mock_commands_products.assert_called_once()
    call_args = mock_commands_products.call_args.args[0]
    assert call_args.product_terms == ["term1", "term2"]


@pytest.mark.parametrize("status_flag", ["-s", "--status"])
@pytest.mark.parametrize("status_value", ["ACTIVE", "INACTIVE", "EXPIRED"])
def test_main_products_status(mock_commands_products, status_flag, status_value):
    result = main(argv=["products", status_flag, status_value])

    assert result == RESULT_SUCCESS
    mock_commands_products.assert_called_once()
    call_args = mock_commands_products.call_args.args[0]
    assert call_args.product_status == status_value


@pytest.mark.parametrize("status_flag", ["-s", "--status"])
def test_main_products_status_unrecognized(mock_commands_products, status_flag):
    with pytest.raises(SystemExit):
        main(argv=["products", status_flag, "UNRECOGNIZED"])

    assert mock_commands_products.call_count == 0


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


@pytest.mark.parametrize("version_flag", ["-v", "--version"])
def test_main_version_flag(version_flag, mocker, capfd, mock_commands_config):
    # littlepay.main.Config (the class)
    config_cls = mocker.patch.object(littlepay.main, "Config")
    # littlepay.main.Config() (an instance)
    config = config_cls.return_value

    with pytest.raises(SystemExit) as err:
        main(argv=[version_flag])
    capture = capfd.readouterr()

    assert err.value.code == RESULT_SUCCESS
    assert re.match(r"littlepay \d+\.\d+\.", capture.out)
    mock_commands_config.assert_not_called()
    # there should have been no calls to any method on littlepay.main.Config()
    assert len(config.mock_calls) == 0
