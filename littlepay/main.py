import sys
from argparse import ArgumentParser, _SubParsersAction

from littlepay import __version__ as version
from littlepay.commands import RESULT_FAILURE
from littlepay.commands.configure import configure
from littlepay.commands.groups import groups
from littlepay.commands.products import products
from littlepay.commands.switch import switch
from littlepay.config import CONFIG_TYPES, Config


def _subcmd(subparsers: _SubParsersAction, name: str, help: str) -> ArgumentParser:
    """Helper creates a new subcommand parser in the collection."""
    parser = subparsers.add_parser(name, help=help)
    return parser


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    main_parser = ArgumentParser(prog="littlepay")

    # https://stackoverflow.com/a/8521644/812183
    # littlepay -v
    # littlepay --version
    main_parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )
    # littlepay -c CONFIG_PATH
    # littlepay --config CONFIG_PATH
    main_parser.add_argument(
        "-c",
        "--config",
        dest="config_path",
        help="Path to a readable and writeable config file to use. File will be created if it does not exist.",
    )

    main_commands = main_parser.add_subparsers(dest="command")

    def _maincmd(name, help):
        return _subcmd(main_commands, name, help)

    # littlepay config [CONFIG_PATH]
    config_parser = _maincmd("config", help="Get or set configuration")
    config_parser.add_argument("config_path", nargs="?")

    # littlepay groups [-f GROUP] [{create,link,products,remove,unlink}] [...]
    groups_parser = _maincmd("groups", help="Interact with groups in the active environment")
    groups_parser.add_argument(
        "-f", "--filter", help="Filter for groups with matching group ID or label", dest="group_terms", action="append"
    )
    groups_parser.add_argument(
        "--csv", action="store_true", default=False, help="Output results in simple CSV format", dest="csv"
    )

    groups_commands = groups_parser.add_subparsers(dest="group_command", required=False)

    groups_create = _subcmd(groups_commands, "create", help="Create a new concession group")
    groups_create.add_argument("group_label", help="A unique label associated with the concession group", metavar="LABEL")

    _subcmd(groups_commands, "funding_sources", help="List funding sources for one or more concession groups")

    groups_link = _subcmd(groups_commands, "link", help="Link one or more concession groups to a product")
    groups_link.add_argument("product_id", help="The ID of the product to link to")

    groups_migrate = _subcmd(
        groups_commands, "migrate", help="Migrate a group from the old Customer Group format to the current format"
    )
    groups_migrate.add_argument(
        "--force", action="store_true", default=False, help="Don't ask for confirmation before migration"
    )

    groups_products = _subcmd(groups_commands, "products", help="List products for one or more concession groups")
    groups_products.add_argument(
        "--csv", action="store_true", default=False, help="Output results in simple CSV format", dest="csv"
    )

    groups_remove = _subcmd(groups_commands, "remove", help="Remove an existing concession group")
    groups_remove.add_argument("--force", action="store_true", default=False, help="Don't ask for confirmation before removal")
    groups_remove.add_argument("group_id", help="The ID of the concession group to remove", metavar="ID")

    groups_unlink = _subcmd(groups_commands, "unlink", help="Unlink a product from one or more concession groups")
    groups_unlink.add_argument("product_id", help="The ID of the product to unlink")

    # littlepay products [-f PRODUCT] [-s STATUS] [{link,unlink}] [...]
    products_parser = _maincmd("products", help="Interact with products in the active environment")
    products_parser.add_argument(
        "-f",
        "--filter",
        help="Filter for products with matching product ID, code, or description",
        dest="product_terms",
        action="append",
    )
    products_parser.add_argument(
        "-s",
        "--status",
        help="Filter for products with matching status",
        choices=["ACTIVE", "INACTIVE", "EXPIRED"],
        dest="product_status",
    )
    products_parser.add_argument(
        "--csv", action="store_true", default=False, help="Output results in simple CSV format", dest="csv"
    )

    products_commands = products_parser.add_subparsers(dest="product_command", required=False)

    products_link = _subcmd(products_commands, "link", help="Link one or more products to a concession group")
    products_link.add_argument("group_id", help="The ID of the concession group to link to")

    products_unlink = _subcmd(products_commands, "unlink", help="Unlink a concession group from one or more products")
    products_unlink.add_argument("group_id", help="The ID of the concession group to unlink")

    # littlepay switch {env, participant} VALUE
    switch_parser = _maincmd("switch", help="Switch the active environment or participant")
    switch_parser.add_argument("switch_type", choices=CONFIG_TYPES, help="The type of object to switch", metavar="TYPE")
    switch_parser.add_argument("switch_arg", help="The new object value", metavar="VALUE")

    args = main_parser.parse_args(argv)

    if args.command == "config" or args.config_path:
        return configure(args.config_path or Config().current_path())
    elif args.command == "groups":
        return groups(args)
    elif args.command == "products":
        return products(args)
    elif args.command == "switch":
        return switch(args.switch_type, args.switch_arg)
    else:
        main_parser.print_help()
        return RESULT_FAILURE


if __name__ == "__main__":
    raise SystemExit(main())
