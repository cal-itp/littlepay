from argparse import Namespace

from littlepay.api.client import Client
from littlepay.api.products import ProductResponse
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS, print_active_message
from littlepay.commands.groups import link_product, unlink_product
from littlepay.config import Config


def products(args: Namespace = None) -> int:
    return_code = RESULT_SUCCESS
    config = Config()
    client = Client.from_active_config(config)

    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    csv_output = hasattr(args, "csv") and args.csv

    if hasattr(args, "product_command"):
        command = args.product_command
    else:
        command = None

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
    if csv_output:
        print(ProductResponse.csv_header())
    else:
        print_active_message(config, f"🛒 Matching products ({len(products)})")

    for product in products:
        if csv_output:
            print(product.csv())
        else:
            print(product)

    if command == "link":
        for product in products:
            return_code += link_product(client, args.group_id, product.id)
    elif command == "unlink":
        for product in products:
            return_code += unlink_product(client, args.group_id, product.id)

    return RESULT_SUCCESS if return_code == RESULT_SUCCESS else RESULT_FAILURE
