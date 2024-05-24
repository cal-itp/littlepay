from argparse import Namespace

import pytest
from requests import HTTPError

from littlepay.api.groups import GroupResponse, GroupFundingSourceResponse
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS
from littlepay.commands.groups import groups

from tests.commands.test_products import PRODUCT_RESPONSES

GROUP_RESPONSES = [
    GroupResponse("id0", "zero", "participant123"),
    GroupResponse("id1", "one", "participant123"),
    GroupResponse("id2", "two", "participant123"),
]

GROUP_FUND_RESPONSES = [
    GroupFundingSourceResponse(
        id="group_funding_id0",
        created_date="2024-04-01T00:05:23Z",
        updated_date="2024-04-02T00:05:23Z",
        expiry_date="2024-04-03T00:05:23Z",
    ),
    GroupFundingSourceResponse(
        id="group_funding_id1",
        created_date="2024-04-04T00:05:23Z",
        updated_date="2024-04-05T00:05:23Z",
        expiry_date="2024-04-06T00:05:23Z",
    ),
    GroupFundingSourceResponse(
        id="group_funding_id2",
        created_date="2024-04-07T00:05:23Z",
        updated_date="2024-04-08T00:05:23Z",
        expiry_date="2024-04-09T00:05:23Z",
    ),
]


@pytest.fixture(autouse=True)
def mock_config(mocker):
    mocker.patch("littlepay.commands.groups.Config")


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    mocker.patch("littlepay.commands.groups.Client.from_active_config", return_value=client)
    return client


@pytest.fixture
def mock_input(mocker):
    def _input(return_value):
        return mocker.patch("littlepay.commands.groups.input", return_value=return_value)

    return _input


@pytest.fixture(autouse=True)
def mock_get_groups(mock_client):
    # return a generator comprehension to mimic how the real function returns a Generator
    mock_client.get_concession_groups.return_value = (r for r in GROUP_RESPONSES)


def test_groups_default(mock_client, capfd):
    res = groups()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    mock_client.oauth.ensure_active_token.assert_called_once()

    assert "Matching groups (3)" in capture.out
    for response in GROUP_RESPONSES:
        assert str(response) in capture.out


def test_groups_csv(mock_client, capfd):
    args = Namespace(csv=True)
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    mock_client.oauth.ensure_active_token.assert_called_once()

    assert "Matching groups (3)" not in capture.out

    assert GroupResponse.csv_header() in capture.out

    for response in GROUP_RESPONSES:
        assert response.csv() in capture.out
        assert str(response) not in capture.out


@pytest.mark.parametrize("group_response", GROUP_RESPONSES)
@pytest.mark.parametrize("filter_attribute", ["id", "label"])
def test_groups_group_terms(group_response, filter_attribute, capfd):
    filter_value = getattr(group_response, filter_attribute)
    args = Namespace(group_terms=[filter_value])
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching groups (1)" in capture.out
    for response in GROUP_RESPONSES:
        if response == group_response:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out


def test_groups_group_terms_multiple(capfd):
    terms = [GROUP_RESPONSES[0].id, GROUP_RESPONSES[1].label]
    args = Namespace(group_terms=terms)
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching groups (2)" in capture.out
    for response in GROUP_RESPONSES:
        if GROUP_RESPONSES.index(response) in [0, 1]:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out


def test_groups_group_command__create(mock_client, capfd):
    args = Namespace(group_command="create", group_label="the-label")
    res = groups(args)
    capture = capfd.readouterr()

    mock_client.create_concession_group.assert_called_once_with("the-label")

    assert res == RESULT_SUCCESS
    assert "Creating group" in capture.out
    assert "Created" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__create_HTTPError(mock_client, capfd):
    mock_client.create_concession_group.side_effect = HTTPError

    args = Namespace(group_command="create", group_label="the-label")
    res = groups(args)
    capture = capfd.readouterr()

    mock_client.create_concession_group.assert_called_once_with("the-label")

    assert res == RESULT_FAILURE
    assert "Creating group" in capture.out
    assert "Error" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__funding_sources(mock_client, capfd):
    mock_client.get_concession_group_linked_funding_sources.return_value = (r for r in GROUP_FUND_RESPONSES)

    args = Namespace(group_command="funding_sources")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Matching groups (3)" in capture.out
    assert "  💵 Linked funding sources (3)" in capture.out


def test_groups_group_command__funding_sources_HTTPError(mock_client, capfd):
    mock_client.get_concession_group_linked_funding_sources.side_effect = HTTPError

    args = Namespace(group_command="funding_sources")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Matching groups (3)" in capture.out
    assert "Error:" in capture.out


def test_groups_group_command__link(mock_client, capfd):
    args = Namespace(group_command="link", product_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    for group in GROUP_RESPONSES:
        mock_client.link_concession_group_product.assert_any_call(group.id, "1234")

    assert res == RESULT_SUCCESS
    assert "Linking group <-> product" in capture.out
    assert "Linked" in capture.out


def test_groups_group_command__link_HTTPError(mock_client, capfd):
    mock_client.link_concession_group_product.side_effect = HTTPError

    args = Namespace(group_command="link", product_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Linking group <-> product" in capture.out
    assert "Error" in capture.out
    assert "Linked" not in capture.out


def test_groups_group_command__products(mock_client, capfd):
    # fake a generator for a single item
    mock_client.get_concession_group_products.return_value = (p for p in PRODUCT_RESPONSES if PRODUCT_RESPONSES.index(p) == 0)

    args = Namespace(group_command="products", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    mock_client.get_concession_group_products.call_count == len(GROUP_RESPONSES)

    assert res == RESULT_SUCCESS
    assert "Linked products (1)" in capture.out
    for product in PRODUCT_RESPONSES:
        if PRODUCT_RESPONSES.index(product) == 0:
            assert str(product) in capture.out
        else:
            assert str(product) not in capture.out


def test_groups_group_command__products_csv(mock_client, capfd):
    # fake a generator for a single item
    mock_client.get_concession_group_products.return_value = (p for p in PRODUCT_RESPONSES if PRODUCT_RESPONSES.index(p) == 0)

    args = Namespace(group_command="products", group_id="1234", csv=True)
    res = groups(args)
    capture = capfd.readouterr()

    mock_client.get_concession_group_products.call_count == len(GROUP_RESPONSES)

    assert res == RESULT_SUCCESS
    assert "Linked products (1)" not in capture.out
    assert "group_id,product_id,participant_id" in capture.out

    for group in GROUP_RESPONSES:
        for product in PRODUCT_RESPONSES:
            assert str(product) not in capture.out
            if GROUP_RESPONSES.index(group) == 0 and PRODUCT_RESPONSES.index(product) == 0:
                assert f"{group.id},{product.id},{group.participant_id}" in capture.out
            else:
                assert f"{group.id},{product.id},{group.participant_id}" not in capture.out


@pytest.mark.parametrize("sample_input", ["y", "Y", "yes", "Yes", "YES"])
def test_groups_group_command__remove_confirm(capfd, mock_input, sample_input):
    mock_input(sample_input)

    args = Namespace(group_command="remove", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Removing group" in capture.out
    assert "Removed" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__remove_confirm_error(capfd, mock_input):
    _input = mock_input(None)
    _input.side_effect = EOFError

    args = Namespace(group_command="remove", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Removing group" in capture.out
    assert "Canceled" in capture.out
    assert "Matching groups (3)" in capture.out


@pytest.mark.parametrize("sample_input", ["n", "N", "no", "No", "NO"])
def test_groups_group_command__remove_decline(capfd, mock_input, sample_input):
    mock_input(sample_input)

    args = Namespace(group_command="remove", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Removing group" in capture.out
    assert "Canceled" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__remove_force(capfd, mock_input):
    _input = mock_input("no")

    args = Namespace(group_command="remove", group_id="1234", force=True)
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert _input.called is False
    assert "Removing group" in capture.out
    assert "Removed" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__remove_HTTPError(capfd, mock_client, mock_input):
    mock_client.remove_concession_group.side_effect = HTTPError
    mock_input("y")

    args = Namespace(group_command="remove", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Removing group" in capture.out
    assert "Error" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__unlink(mock_client, capfd):
    args = Namespace(group_command="unlink", product_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    for group in GROUP_RESPONSES:
        mock_client.unlink_concession_group_product.assert_any_call(group.id, "1234")

    assert res == RESULT_SUCCESS
    assert "Unlinking group <-> product" in capture.out
    assert "Unlinked" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__unlink_HTTPError(mock_client, capfd):
    mock_client.unlink_concession_group_product.side_effect = HTTPError

    args = Namespace(group_command="unlink", product_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Unlinking group <-> product" in capture.out
    assert "Error" in capture.out
    assert "Unlinked" not in capture.out


@pytest.mark.parametrize("sample_input", ["y", "Y", "yes", "Yes", "YES"])
def test_groups_group_command__migrate_confirm(mock_client, capfd, mock_input, sample_input):
    mock_input(sample_input)

    args = Namespace(group_command="migrate")
    res = groups(args)
    capture = capfd.readouterr()

    for group in GROUP_RESPONSES:
        mock_client.migrate_concession_group.assert_any_call(group.id)

    assert res == RESULT_SUCCESS
    assert "Migrating group" in capture.out
    assert "Migrated" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__migrate_confirm_error(capfd, mock_input):
    _input = mock_input(None)
    _input.side_effect = EOFError

    args = Namespace(group_command="migrate")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Migrating group" in capture.out
    assert "Canceled" in capture.out
    assert "Matching groups (3)" in capture.out


@pytest.mark.parametrize("sample_input", ["n", "N", "no", "No", "NO"])
def test_groups_group_command__migrate_decline(capfd, mock_input, sample_input):
    mock_input(sample_input)

    args = Namespace(group_command="migrate")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    assert "Migrating group" in capture.out
    assert "Canceled" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__migrate_force(mock_client, capfd, mock_input):
    _input = mock_input("no")

    args = Namespace(group_command="migrate", force=True)
    res = groups(args)
    capture = capfd.readouterr()

    for group in GROUP_RESPONSES:
        mock_client.migrate_concession_group.assert_any_call(group.id)

    assert res == RESULT_SUCCESS
    assert _input.called is False
    assert "Migrating group" in capture.out
    assert "Migrated" in capture.out
    assert "Matching groups (3)" in capture.out


def test_groups_group_command__migrate_HTTPError(mock_client, capfd, mock_input):
    mock_client.migrate_concession_group.side_effect = HTTPError
    mock_input("y")

    args = Namespace(group_command="migrate", group_id="1234")
    res = groups(args)
    capture = capfd.readouterr()

    assert res == RESULT_FAILURE
    assert "Migrating group" in capture.out
    assert "Error" in capture.out
    assert "Matching groups (3)" in capture.out
