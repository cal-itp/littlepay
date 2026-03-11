from argparse import Namespace

from requests import HTTPError

from littlepay.api.client import Client
from littlepay.api.groups import GroupResponse
from littlepay.commands import RESULT_FAILURE, RESULT_SUCCESS, print_active_message
from littlepay.config import Config


def _get_groups(args: Namespace, client: Client) -> list:
    """Get a list of groups for the current Client, optionally filtered by term"""

    groups = client.get_concession_groups()

    if group_terms := getattr(args, "group_terms", None):
        terms = [t.lower() for t in group_terms if t]
        groups = filter(
            lambda g: any([term in g.id.lower() or term in g.label.lower() for term in terms]),
            groups,
        )

    return list(groups)


def _list_results(args: Namespace, client: Client, config: Config, groups: list, command: str) -> None:
    """Print a list of groups and possibly their products or funding sources"""

    return_code = RESULT_SUCCESS
    csv_output = getattr(args, "csv", False)

    if not csv_output:
        print_active_message(config, f"👥 Matching groups ({len(groups)})")

    match command:
        case "products":
            if csv_output:
                # print a custom CSV header for group<>product associations
                print("group_id,product_id,participant_id")
            for group in groups:
                products = list(client.get_concession_group_products(group.id))
                if not csv_output:
                    print(group)
                    print(f"  🛒 Linked products ({len(products)})")
                    for product in products:
                        print(" ", product)
                else:
                    for product in products:
                        print(f"{group.id},{product.id},{group.participant_id}")
        case "funding_sources":
            if csv_output:
                # print a custom CSV header for group<>funding_source associations
                print("group_id,funding_source_id,participant_id")
            for group in groups:
                if not csv_output:
                    print(group)
                return_code += funding_sources(client, group, csv_output)
        case _:
            if csv_output:
                print(GroupResponse.csv_header())
            for group in groups:
                print(group.csv()) if csv_output else print(group)

    return return_code


def groups(args: Namespace = None) -> int:
    return_code = RESULT_SUCCESS
    config = Config()
    client = Client.from_active_config(config)

    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    # Get list of groups
    groups = _get_groups(args, client)

    # Handle subcommand, if present
    command = getattr(args, "group_command", None)

    match command:
        case "create":
            return_code += create_group(client, args.group_label)
            groups = _get_groups(args, client)  # Updating list after creating the new one
        case "remove":
            return_code += remove_group(client, args.group_id, getattr(args, "force", False))
            groups = _get_groups(args, client)  # Updating list after removing the old one
        case "link":
            for group in groups:
                return_code += link_product(client, group.id, args.product_id)
        case "unlink":
            if getattr(args, "product", None):
                for group in groups:
                    return_code += unlink_product(client, group.id, args.product)
            elif getattr(args, "source", None):
                for group in groups:
                    return_code += unlink_funding_source(client, group.id, args.source)
        case "migrate":
            for group in groups:
                return_code += migrate_group(client, group.id, getattr(args, "force", False))

    # Output resulting list
    return_code += _list_results(args, client, config, groups, command)

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


def unlink_funding_source(client: Client, group_id: str, funding_source_id: str) -> int:
    config = Config()
    print_active_message(config, "Unlinking group <-> funding source", f"[{group_id}] <-> [{funding_source_id}]")
    return_code = RESULT_SUCCESS

    try:
        client.unlink_concession_group_funding_source(group_id, funding_source_id)
        print("✅ Unlinked funding source")
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


def funding_sources(client: Client, group: GroupResponse, csv_output: bool) -> int:
    return_code = RESULT_SUCCESS

    try:
        funding_sources = client.get_concession_group_linked_funding_sources(group.id)
        funding_sources = list(funding_sources)
        if not csv_output:
            print(f"  💵 Linked funding sources ({len(funding_sources)})")
        for funding_source in funding_sources:
            if csv_output:
                print(f"{group.id},{funding_source.id},{group.participant_id}")
            else:
                print(" ", funding_source)
    except HTTPError as err:
        print(f"❌ Error: {err}")
        return_code = RESULT_FAILURE

    return return_code
