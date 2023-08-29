from argparse import _SubParsersAction, ArgumentParser
import sys

from littlepay import __version__ as version
from littlepay.commands.configure import configure
from littlepay.commands.groups import groups
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
    config_parser = _maincmd("config", help="Get or set configuration.")
    config_parser.add_argument("config_path", nargs="?", default=Config.current_path())

    # littlepay groups [-f GROUP]
    groups_parser = _maincmd("groups", help="Get information about groups in the active environment.")
    groups_parser.add_argument("-f", "--filter", help="Filter for groups with matching group ID or label", dest="group")
    _ = groups_parser.add_subparsers(dest="group_command", required=False)

    # littlepay switch {env, participant} VALUE
    switch_parser = _maincmd("switch", help="Switch the active environment or participant.")
    switch_parser.add_argument("switch_type", choices=CONFIG_TYPES, help="The type of object to switch", metavar="TYPE")
    switch_parser.add_argument("switch_arg", help="The new object value", metavar="VALUE")

    if len(argv) == 0:
        argv = ["config"]

    args = main_parser.parse_args(argv)

    if args.command == "config" or args.config_path:
        return configure(args.config_path)
    elif args.command == "groups":
        return groups(
            getattr(args, "group", None),
            getattr(args, "group_command", None),
            funding_source_id=getattr(args, "funding_source_id", None),
        )
    elif args.command == "switch":
        return switch(args.switch_type, args.switch_arg)


if __name__ == "__main__":
    raise SystemExit(main())
