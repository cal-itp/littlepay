from argparse import Namespace

import pytest

from littlepay.api.products import ProductResponse
from littlepay.commands import RESULT_SUCCESS
from littlepay.commands.products import products

PRODUCT_RESPONSES = [
    ProductResponse("id0", "code0", "ACTIVE", "type0", "description0", "participant123"),
    ProductResponse("id1", "code1", "INACTIVE", "type1", "description1", "participant123"),
    ProductResponse("id2", "code2", "EXPIRED", "type2", "description2", "participant123"),
    ProductResponse("id3", "code3", "EXPIRED", "type3", "description3", "participant123"),
]


@pytest.fixture(autouse=True)
def mock_config(mocker):
    mocker.patch("littlepay.commands.products.Config")


@pytest.fixture
def mock_client(mocker):
    client = mocker.Mock()
    mocker.patch("littlepay.commands.products.Client.from_active_config", return_value=client)
    return client


@pytest.fixture(autouse=True)
def mock_get_products(mock_client):
    mock_client.get_products.return_value = PRODUCT_RESPONSES


def test_products_default(mock_client, capfd):
    res = products()
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    mock_client.oauth.ensure_active_token.assert_called_once()
    mock_client.get_products.assert_called_with(status=None)

    assert "Matching products (4)" in capture.out
    for response in PRODUCT_RESPONSES:
        assert str(response) in capture.out


def test_products_csv(mock_client, capfd):
    args = Namespace(csv=True)
    res = products(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    mock_client.oauth.ensure_active_token.assert_called_once()
    mock_client.get_products.assert_called_with(status=None)

    assert "Matching products (4)" not in capture.out

    assert ProductResponse.csv_header() in capture.out

    for response in PRODUCT_RESPONSES:
        assert response.csv() in capture.out
        assert str(response) not in capture.out


def test_products_product_command__link(mock_client, capfd):
    args = Namespace(product_command="link", group_id="1234")
    res = products(args)
    capture = capfd.readouterr()

    for product in PRODUCT_RESPONSES:
        mock_client.link_concession_group_product.assert_any_call("1234", product.id)

    assert res == RESULT_SUCCESS
    assert "Linking group <-> product" in capture.out
    assert "Linked" in capture.out


def test_products_product_command__unlink(mock_client, capfd):
    args = Namespace(product_command="unlink", group_id="1234")
    res = products(args)
    capture = capfd.readouterr()

    for product in PRODUCT_RESPONSES:
        mock_client.unlink_concession_group_product.assert_any_call("1234", product.id)

    assert res == RESULT_SUCCESS
    assert "Unlinking group <-> product" in capture.out
    assert "Unlinked" in capture.out


@pytest.mark.parametrize("product_response", PRODUCT_RESPONSES)
def test_products_product_status(mock_client, product_response, capfd):
    args = Namespace(product_status=product_response.status)
    res = products(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS
    mock_client.get_products.assert_called_with(status=product_response.status)

    assert "Matching products" in capture.out


@pytest.mark.parametrize("product_response", PRODUCT_RESPONSES)
@pytest.mark.parametrize("filter_attribute", ["id", "code", "description"])
def test_products_product_term(product_response, filter_attribute, capfd):
    filter_value = getattr(product_response, filter_attribute)
    args = Namespace(product_terms=[filter_value])
    res = products(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching products (1)" in capture.out
    for response in PRODUCT_RESPONSES:
        if response == product_response:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out


def test_products_product_term_multiple(capfd):
    terms = [PRODUCT_RESPONSES[0].id, PRODUCT_RESPONSES[1].code, PRODUCT_RESPONSES[2].description]
    args = Namespace(product_terms=terms)
    res = products(args)
    capture = capfd.readouterr()

    assert res == RESULT_SUCCESS

    assert "Matching products (3)" in capture.out
    for response in PRODUCT_RESPONSES:
        if PRODUCT_RESPONSES.index(response) in [0, 1, 2]:
            assert str(response) in capture.out
        else:
            assert str(response) not in capture.out
