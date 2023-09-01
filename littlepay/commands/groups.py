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

    if hasattr(args, "group_term") and args.group_term is not None:
        term = args.group_term.lower()
        groups = filter(
            lambda g: term in g.id.lower() or term in g.label.lower(),
            groups,
        )

    groups = list(groups)
    print_active_message(config, f"👥 Matching groups ({len(groups)})")

    for group in groups:
        print(group)

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
