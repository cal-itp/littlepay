from argparse import Namespace

from littlepay.api.client import Client
from littlepay.commands import RESULT_SUCCESS, print_active_message
from littlepay.config import Config

config = Config()


def products(args: Namespace = None) -> int:
    client = Client.from_active_config(config)
    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    if hasattr(args, "product_status") and args.product_status is not None:
        status = args.product_status
    else:
        status = None

    products = client.get_products(status=status)

    if hasattr(args, "product_terms") and args.product_terms is not None:
        terms = [t.lower() for t in args.product_terms if t]
        products = filter(
            lambda p: any(
                [any((term in p.id.lower(), term in p.code.lower(), term in p.description.lower())) for term in terms]
            ),
            products,
        )

    products = list(products)
    print_active_message(config, f"🛒 Matching products ({len(products)})")

    for product in products:
        print(product)

    return RESULT_SUCCESS
