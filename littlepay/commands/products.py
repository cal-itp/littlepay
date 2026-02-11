from argparse import Namespace

from littlepay.api.client import Client
from littlepay.api.products import ProductResponse
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS, print_active_message
from littlepay.commands.groups import link_product, unlink_product
from littlepay.config import Config


def _get_products(args: Namespace, client: Client) -> list:
    """Get a list of products for the current Client, optionally filtered by status and filter"""

    status = getattr(args, "product_status", None)
    products = client.get_products(status=status)

    if product_terms := getattr(args, "product_terms", None):
        terms = [t.lower() for t in product_terms if t]
        products = filter(
            lambda p: any(
                [any((term in p.id.lower(), term in p.code.lower(), term in p.description.lower())) for term in terms]
            ),
            products,
        )

    return list(products)


def _list_products(args: Namespace, config: Config, products: list) -> None:
    """Print a list of products, optionally in CSV format"""

    csv_output = getattr(args, "csv", False)

    if csv_output:
        print(ProductResponse.csv_header())
    else:
        print_active_message(config, f"🛒 Matching products ({len(products)})")

    for product in products:
        if csv_output:
            print(product.csv())
        else:
            print(product)


def products(args: Namespace = None) -> int:
    return_code = RESULT_SUCCESS
    config = Config()
    client = Client.from_active_config(config)

    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    if hasattr(args, "product_command"):
        command = args.product_command
    else:
        command = None

    products = _get_products(args, client)
    _list_products(args, config, products)

    if command == "link":
        for product in products:
            return_code += link_product(client, args.group_id, product.id)
    elif command == "unlink":
        for product in products:
            return_code += unlink_product(client, args.group_id, product.id)

    return RESULT_SUCCESS if return_code == RESULT_SUCCESS else RESULT_FAILURE
