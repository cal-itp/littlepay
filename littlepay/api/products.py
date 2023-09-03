from dataclasses import dataclass
from typing import Generator

from littlepay.api import ClientProtocol
from littlepay.api.groups import GroupsMixin


@dataclass
class ProductResponse:
    id: str
    code: str
    status: str
    type: str
    description: str
    participant_id: str


class ProductsMixin(GroupsMixin, ClientProtocol):
    """Mixin implements APIs for products."""

    PRODUCTS = "products"

    def concession_group_products_endpoint(self, group_id: str, product_id: str = None) -> str:
        """Endpoint for a concession group's products. Optionally provide a product_id for a product-specific endpoint."""
        return self.concession_groups_endpoint(group_id, self.PRODUCTS, product_id)

    def get_concession_group_products(self, group_id: str) -> Generator[ProductResponse, None, None]:
        """Yield ProductResponse objects from the concession_group's products endpoint."""
        endpoint = self.concession_group_products_endpoint(group_id)
        for item in self._get_list(endpoint):
            for product in self.get_products(item["id"]):
                yield product

    def get_products(self, product_id: str = None, status: str = None) -> Generator[ProductResponse, None, None]:
        """Yield ProductResponse objects from the products endpoint."""
        endpoint = self.products_endpoint(product_id)
        if product_id is None:
            for item in self._get_list(endpoint, status=status):
                yield ProductResponse(**item)
        else:
            yield self._get(endpoint, ProductResponse)

    def products_endpoint(self, product_id: str = None) -> str:
        """Endpoint for products."""
        return self._make_endpoint(self.PRODUCTS, product_id)
