from dataclasses import dataclass
from typing import Generator

from littlepay.api import ClientProtocol


@dataclass
class ProductResponse:
    id: str
    code: str
    status: str
    type: str
    description: str
    participant_id: str


class ProductsMixin(ClientProtocol):
    """Mixin implements APIs for products."""

    PRODUCTS = "products"

    def get_products(self, product_id: str = None, status: str = None) -> Generator[ProductResponse, None, None]:
        """Yield ProductResponse objects from the products endpoint."""
        endpoint = self.products_endpoint(product_id)
        for item in self._get_list(endpoint, status=status):
            yield ProductResponse(**item)

    def products_endpoint(self, product_id: str = None) -> str:
        """Endpoint for products."""
        return self._make_endpoint(self.PRODUCTS, product_id)
