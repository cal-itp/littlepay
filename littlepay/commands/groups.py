from argparse import Namespace

from requests import HTTPError

from littlepay.api.client import Client
from littlepay.api.groups import GroupResponse
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS, print_active_message
from littlepay.config import Config


def groups(args: Namespace = None) -> int:
    return_code = RESULT_SUCCESS
    config = Config()
    client = Client.from_active_config(config)

    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    csv_output = hasattr(args, "csv") and args.csv

    if hasattr(args, "group_command"):
        command = args.group_command
    else:
        command = None

    if command == "create":
        return_code += create_group(client, args.group_label)
    elif command == "remove":
        return_code += remove_group(client, args.group_id, getattr(args, "force", False))

    groups = client.get_concession_groups()

    if hasattr(args, "group_terms") and args.group_terms is not None:
        terms = [t.lower() for t in args.group_terms if t]
        groups = filter(
            lambda g: any([term in g.id.lower() or term in g.label.lower() for term in terms]),
            groups,
        )

    groups = list(groups)

    if command == "link":
        for group in groups:
            return_code += link_product(client, group.id, args.product_id)
    elif command == "unlink":
        for group in groups:
            return_code += unlink_product(client, group.id, args.product_id)
    elif command == "migrate":
        for group in groups:
            return_code += migrate_group(client, group.id, getattr(args, "force", False))

    if csv_output and command != "products":
        print(GroupResponse.csv_header())
    elif csv_output and command == "products":
        # print a custom CSV header for group<>product associations
        print("group_id,product_id,participant_id")
    else:
        print_active_message(config, f"👥 Matching groups ({len(groups)})")

    for group in groups:
        if not csv_output:
            print(group)
        if command == "products":
            products = list(client.get_concession_group_products(group.id))
            if not csv_output:
                print(f"  🛒 Linked products ({len(products)})")
            for product in products:
                if csv_output:
                    print(f"{group.id},{product.id},{group.participant_id}")
                else:
                    print(" ", product)
        elif command == "funding_sources":
            return_code += funding_sources(client, group.id)
        elif csv_output:
            print(group.csv())

    return RESULT_SUCCESS if return_code == RESULT_SUCCESS else RESULT_FAILURE


def create_group(client: Client, group_label: str) -> int:
    config = Config()
    print_active_message(config, "Creating group", f"[{group_label}]")
    return_code = RESULT_SUCCESS

    try:
        result = client.create_concession_group(group_label)
        print(f"✅ Created: {result}")
    except HTTPError as err:
        print(f"❌ Error: {err}")
        return_code = RESULT_FAILURE

    return return_code


def remove_group(client: Client, group_id: str, force: bool = False) -> int:
    config = Config()
    print_active_message(config, "Removing group", f"[{group_id}]")
    return_code = RESULT_SUCCESS

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
            return_code = RESULT_FAILURE
    else:
        print("Canceled...")

    return return_code


def link_product(client: Client, group_id: str, product_id: str) -> int:
    config = Config()
    print_active_message(config, "Linking group <-> product", f"[{group_id}] <-> [{product_id}]")
    return_code = RESULT_SUCCESS

    try:
        result = client.link_concession_group_product(group_id, product_id)
        print(f"✅ Linked: {result}")
    except HTTPError as err:
        print(f"❌ Error: {err}")
        return_code = RESULT_FAILURE

    return return_code


def unlink_product(client: Client, group_id: str, product_id: str) -> int:
    config = Config()
    print_active_message(config, "Unlinking group <-> product", f"[{group_id}] <-> [{product_id}]")
    return_code = RESULT_SUCCESS

    try:
        client.unlink_concession_group_product(group_id, product_id)
        print("✅ Unlinked")
    except HTTPError as err:
        print(f"❌ Error: {err}")
        return_code = RESULT_FAILURE

    return return_code


def migrate_group(client: Client, group_id: str, force: bool = False) -> int:
    config = Config()
    print_active_message(config, "Migrating group", f"[{group_id}]")
    return_code = RESULT_SUCCESS

    if force is True:
        confirm = "yes"
    else:
        try:
            confirm = input("❔ Are you sure? (yes/no): ")
        except EOFError:
            confirm = "no"

    if confirm.lower().startswith("y"):
        print("Migrating group...")
        try:
            client.migrate_concession_group(group_id)
            print("✅ Migrated")
        except HTTPError as err:
            print(f"❌ Error: {err}")
            return_code = RESULT_FAILURE
    else:
        print("Canceled...")

    return return_code


def funding_sources(client: Client, group_id: str) -> int:
    return_code = RESULT_SUCCESS

    try:
        funding_sources = client.get_concession_group_linked_funding_sources(group_id)
        funding_sources = list(funding_sources)
        print(f"  💵 Linked funding sources ({len(funding_sources)})")
        for funding_source in funding_sources:
            print(" ", funding_source)
    except HTTPError as err:
        print(f"❌ Error: {err}")
        return_code = RESULT_FAILURE

    return return_code
