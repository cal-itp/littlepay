from argparse import Namespace
import pytest

from littlepay.api.groups import GroupResponse
from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.groups import groups

GROUP_RESPONSES = [
    GroupResponse("id0", "zero", "participant123"),
    GroupResponse("id1", "one", "participant123"),
    GroupResponse("id2", "two", "participant123"),
]


@pytest.fixture(autouse=True)
def mock_config(mocker):
    mocker.patch("littlepay.commands.groups.config")


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    mocker.patch("littlepay.commands.groups.Client.from_active_config", return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_get_groups(mock_client):
    mock_client.get_concession_groups.return_value = GROUP_RESPONSES


def test_groups_default(mock_client, capfd):
    res = groups()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    mock_client.oauth.ensure_active_token.assert_called_once()

    assert "Matching groups (3)" in capture.out
    for response in GROUP_RESPONSES:
        assert str(response) in capture.out


@pytest.mark.parametrize("group_response", GROUP_RESPONSES)
def test_groups_group_term__group_id(group_response, capfd):
    args = Namespace(group_term=group_response.id)
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching groups (1)" in capture.out
    for response in GROUP_RESPONSES:
        if response == group_response:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out


@pytest.mark.parametrize("group_response", GROUP_RESPONSES)
def test_groups_group_term__group_label(group_response, capfd):
    args = Namespace(group_term=group_response.label)
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching groups (1)" in capture.out
    for response in GROUP_RESPONSES:
        if response == group_response:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out
