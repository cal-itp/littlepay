from argparse import Namespace

from requests import HTTPError

from littlepay.api.client import Client
from littlepay.commands import RESULT_SUCCESS, print_active_message
from littlepay.config import Config

config = Config()


def groups(args: Namespace = None) -> int:
    client = Client.from_active_config(config)
    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    if hasattr(args, "group_command"):
        command = args.group_command
    else:
        command = None

    if command == "create":
        create_group(client, args.group_label)
    elif command == "remove":
        remove_group(client, args.group_id, getattr(args, "force", False))

    groups = client.get_concession_groups()

    if hasattr(args, "group_terms") and args.group_terms is not None:
        terms = [t.lower() for t in args.group_terms if t]
        groups = filter(
            lambda g: any([term in g.id.lower() or term in g.label.lower() for term in terms]),
            groups,
        )

    if command == "link":
        for group in groups:
            link_product(client, group.id, args.product_id)
    elif command == "unlink":
        for group in groups:
            unlink_product(client, group.id, args.product_id)

    groups = list(groups)
    print_active_message(config, f"👥 Matching groups ({len(groups)})")

    for group in groups:
        print(group)
        if command == "products":
            products = list(client.get_concession_group_products(group.id))
            print(f"  🛒 Linked products ({len(products)})")
            for product in products:
                print(" ", product)

    return RESULT_SUCCESS


def create_group(client: Client, group_label: str):
    print_active_message(config, "Creating group", f"[{group_label}]")

    try:
        result = client.create_concession_group(group_label)
        print(f"✅ Created: {result}")
    except HTTPError as err:
        print(f"❌ Error: {err}")


def remove_group(client: Client, group_id: str, force: bool = False):
    print_active_message(config, "Removing group", f"[{group_id}]")

    if force is True:
        confirm = "yes"
    else:
        try:
            confirm = input("❔ Are you sure? (yes/no): ")
        except EOFError:
            confirm = "no"

    if confirm.lower().startswith("y"):
        print("Removing group...")
        try:
            client.remove_concession_group(group_id)
            print("✅ Removed")
        except HTTPError as err:
            print(f"❌ Error: {err}")
    else:
        print("Canceled...")


def link_product(client: Client, group_id: str, product_id: str):
    print_active_message(config, "Linking group <-> product", f"[{group_id}] <-> [{product_id}]")

    try:
        result = client.link_concession_group_product(group_id, product_id)
        print(f"✅ Linked: {result}")
    except HTTPError as err:
        print(f"❌ Error: {err}")


def unlink_product(client: Client, group_id: str, product_id: str):
    print_active_message(config, "Unlinking group <-> product", f"[{group_id}] <-> [{product_id}]")

    try:
        client.unlink_concession_group_product(group_id, product_id)
        print("✅ Unlinked")
    except HTTPError as err:
        print(f"❌ Error: {err}")
