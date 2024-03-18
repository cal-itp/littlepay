from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator

from littlepay.api import ClientProtocol
from littlepay.api.funding_sources import FundingSourcesMixin


@dataclass
class GroupResponse:
    id: str
    label: str
    participant_id: str

    def csv(self) -> str:
        """Get a CSV str representation of values for this GroupResponse."""
        # wrap values containing commas in double quotes
        vals = [f'"{v}"' if "," in v else v for v in vars(self).values()]
        return ",".join(vals)

    @staticmethod
    def csv_header() -> str:
        """Get a CSV str header of attributes for GroupResponse."""
        instance = GroupResponse("", "", "")
        return ",".join(vars(instance).keys())


class GroupsMixin(ClientProtocol):
    """Mixin implements APIs for concession groups."""

    CONCESSION_GROUPS = "concession_groups"

    def _format_concession_expiry(self, concession_expiry: datetime):
        """Formats a concession expiry datetime into a string suitable for using in an API request body."""
        if not isinstance(concession_expiry, datetime):
            raise TypeError("concession_expiry must be a Python datetime instance")
        # determine if concession_expiry is an "aware" or "naive" datetime instance
        # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
        if concession_expiry.tzinfo is not None and concession_expiry.tzinfo.utcoffset(concession_expiry) is not None:
            # concession_expiry is an "aware" datetime instance, meaning it has associated time zone information
            # ensure this datetime instance is expressed in UTC
            concession_expiry = concession_expiry.astimezone(timezone.utc)
        else:
            # concession_expiry is a "naive" datetime instance, meaning it has no associated time zone information
            # assume this datetime instance was provided in UTC
            concession_expiry = concession_expiry.replace(tzinfo=timezone.utc)
        # now concession_expiry is an "aware" datetime instance in UTC, format and add to the payload
        # datetime.isoformat() adds the UTC offset like +00:00
        # so keep everything but the last 6 characters and add the Z offset character
        return f"{concession_expiry.isoformat(timespec='seconds')[:-6]}Z"

    def concession_groups_endpoint(self, group_id: str = None, *parts: str) -> str:
        """Endpoint for concession groups. Optionally provide a group_id for a group-specific endpoint."""
        return self._make_endpoint(self.CONCESSION_GROUPS, group_id, *parts)

    def concession_group_funding_source_endpoint(self, group_id: str) -> str:
        """Endpoint for a concession group's funding sources."""
        return self.concession_groups_endpoint(group_id, FundingSourcesMixin.FUNDING_SOURCES)

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

    def link_concession_group_funding_source(
        self, group_id: str, funding_source_id: str, concession_expiry: datetime = None
    ) -> dict:
        """Link a funding source to a concession group."""
        endpoint = self.concession_group_funding_source_endpoint(group_id)
        data = {"id": funding_source_id}

        if concession_expiry is not None:
            data["concession_expiry"] = self._format_concession_expiry(concession_expiry)

        return self._post(endpoint, data, dict)

        return self._post(endpoint, data, dict)
