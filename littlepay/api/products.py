from dataclasses import dataclass
from typing import Generator

from littlepay.api import ClientProtocol, from_kwargs
from littlepay.api.groups import GroupsMixin


@dataclass
class ProductResponse:
    id: str
    code: str
    status: str
    type: str
    description: str
    participant_id: str

    def csv(self) -> str:
        """Get a CSV str representation of values for this ProductResponse."""
        # wrap values containing commas in double quotes
        vals = [f'"{v}"' if "," in v else v for v in vars(self).values()]
        return ",".join(vals)

    @staticmethod
    def csv_header() -> str:
        """Get a CSV str header of attributes for ProductResponse."""
        instance = ProductResponse("", "", "", "", "", "")
        return ",".join(vars(instance).keys())

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)


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
            for item in self._get_list(endpoint, status=status, perPage=100):
                yield ProductResponse(**item)
        else:
            yield self._get(endpoint, ProductResponse)

    def link_concession_group_product(self, group_id: str, product_id: str) -> dict:
        """Link a product to a concession group."""
        endpoint = self.concession_group_products_endpoint(group_id)
        data = {"id": product_id}
        return self._post(endpoint, data, dict)

    def products_endpoint(self, product_id: str = None) -> str:
        """Endpoint for products."""
        return self._make_endpoint(self.PRODUCTS, product_id)

    def unlink_concession_group_product(self, group_id: str, product_id: str) -> bool:
        """Unlink a product from a concession group."""
        endpoint = self.concession_group_products_endpoint(group_id, product_id)
        return self._delete(endpoint)
