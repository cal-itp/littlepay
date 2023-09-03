from typing import Generator

import pytest

from littlepay.api.products import ProductsMixin, ProductResponse

PRODUCTS = [
    dict(id="0", code="zero", status="ACTIVE", type="CAPPING", description="zero cap", participant_id="zero_0"),
    dict(id="1", code="one", status="INACTIVE", type="DISCOUNT", description="one discount", participant_id="one_1"),
    dict(id="2", code="two", status="EXPIRED", type="CAPPING", description="two expired caps", participant_id="two_2"),
]


@pytest.fixture
def mock_ClientProtocol_get_list(mocker):
    return mocker.patch("littlepay.api.ClientProtocol._get_list", side_effect=lambda *args, **kwargs: (g for g in PRODUCTS))


@pytest.fixture
def mock_ClientProtocol_get_list_ProductResponse(mocker):
    return mocker.patch(
        "littlepay.api.ClientProtocol._get_list", side_effect=lambda *args, **kwargs: (ProductResponse(**p) for p in PRODUCTS)
    )


@pytest.fixture
def mock_ClientProtocol_get_Product(mocker):
    return mocker.patch(
        "littlepay.api.ClientProtocol._get", side_effect=lambda *args, **kwargs: (ProductResponse(**p) for p in PRODUCTS[0:1])
    )


@pytest.fixture
def mock_ProductsMixin_get_products(mocker):
    return mocker.patch(
        "littlepay.api.products.ProductsMixin.get_products",
        # fake a generator for a single item
        side_effect=lambda item_id: (ProductResponse(**item) for item in PRODUCTS if item["id"] == item_id),
    )


def test_ProductsMixin_concession_groups_products_endpoint(url):
    client = ProductsMixin()

    assert client.concession_group_products_endpoint("1234") == f"{url}/concession_groups/1234/products"


def test_ProductsMixin_concession_groups_products_endpoint_product_id(url):
    client = ProductsMixin()

    assert client.concession_group_products_endpoint("1234", "5678") == f"{url}/concession_groups/1234/products/5678"


def test_ProductsMixin_get_concession_group_products(mock_ClientProtocol_get_list, mock_ProductsMixin_get_products):
    client = ProductsMixin()

    result = client.get_concession_group_products("1234")
    assert isinstance(result, Generator)
    assert mock_ClientProtocol_get_list.call_count == 0
    assert mock_ProductsMixin_get_products.call_count == 0

    result_list = list(result)
    mock_ClientProtocol_get_list.assert_called_once_with(client.concession_group_products_endpoint("1234"))
    assert mock_ProductsMixin_get_products.call_count == len(PRODUCTS)
    assert len(result_list) == len(PRODUCTS)
    assert all([isinstance(item, ProductResponse) for item in result_list])


def test_ProductsMixin_get_products(mock_ClientProtocol_get_list):
    client = ProductsMixin()

    result = client.get_products()
    assert isinstance(result, Generator)
    assert mock_ClientProtocol_get_list.call_count == 0

    result_list = list(result)
    mock_ClientProtocol_get_list.assert_called_once_with(client.products_endpoint(), status=None)
    assert len(result_list) == len(PRODUCTS)
    assert all([isinstance(item, ProductResponse) for item in result_list])


def test_ProductsMixin_get_products_product_id(url, mock_ClientProtocol_get_Product):
    client = ProductsMixin()

    result = client.get_products("1234")
    assert isinstance(result, Generator)

    for _ in result:
        mock_ClientProtocol_get_Product.assert_called_once_with(f"{url}/products/1234", ProductResponse)


def test_ProductsMixin_products_endpoint(url):
    client = ProductsMixin()

    assert client.products_endpoint() == f"{url}/products"


def test_ProductsMixin_products_endpoint_id(url):
    client = ProductsMixin()

    assert client.products_endpoint("1234") == f"{url}/products/1234"
