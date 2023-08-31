from dataclasses import dataclass
from typing import Generator

from littlepay.api import ClientProtocol


@dataclass
class GroupResponse:
    id: str
    label: str
    participant_id: str


class GroupsMixin(ClientProtocol):
    """Mixin implements APIs for concession groups."""

    CONCESSION_GROUPS = "concession_groups"

    def concession_groups_endpoint(self, group_id: str = None, *parts: str) -> str:
        """Endpoint for concession groups. Optionally provide a group_id for a group-specific endpoint."""
        return self._make_endpoint(self.CONCESSION_GROUPS, group_id, *parts)

    def create_concession_group(self, group_label: str) -> dict:
        """Create a new concession group."""
        endpoint = self.concession_groups_endpoint()
        data = {"label": group_label}
        return self._post(endpoint, data, dict)

    def get_concession_groups(self) -> Generator[GroupResponse, None, None]:
        """Yield GroupResponse objects from the concession_groups endpoint."""
        endpoint = self.concession_groups_endpoint()
        for item in self._get_list(endpoint):
            yield GroupResponse(**item)

    def remove_concession_group(self, group_id) -> bool:
        """Remove an existing concession group."""
        endpoint = self.concession_groups_endpoint(group_id)
        return self._delete(endpoint)
