from littlepay.api.client import Client
from littlepay.commands import RESULT_SUCCESS
from littlepay.config import Config


def groups(group_term: str = None, group_command: str = None, **kwargs) -> int:
    config = Config()
    client = Client.from_active_config(config)
    client.oauth.ensure_active_token(client.token)
    config.active_token = client.token

    groups = client.get_concession_groups()

    if group_term is not None:
        term = group_term.lower()
        groups = filter(
            lambda g: term in g.id.lower() or term in g.label.lower(),
            groups,
        )

    groups = list(groups)
    print(f"👥 Matching groups ({len(groups)})")

    for group in groups:
        print(group)

    return RESULT_SUCCESS
