from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Generator

from littlepay.api import ClientProtocol, from_kwargs
from littlepay.api.funding_sources import FundingSourceDateFields, FundingSourcesMixin


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

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)


@dataclass(kw_only=True)
class GroupFundingSourceResponse(FundingSourceDateFields):
    id: str

    @classmethod
    def from_kwargs(cls, **kwargs):
        return from_kwargs(cls, **kwargs)


class GroupsMixin(ClientProtocol):
    """Mixin implements APIs for concession groups."""

    CONCESSION_GROUPS = "concession_groups"

    def _format_expiry(self, expiry: datetime):
        """Formats an expiry datetime into a string suitable for using in an API request body."""
        if not isinstance(expiry, datetime):
            raise TypeError("expiry must be a Python datetime instance")
        # determine if expiry is an "aware" or "naive" datetime instance
        # https://docs.python.org/3/library/datetime.html#determining-if-an-object-is-aware-or-naive
        if expiry.tzinfo is not None and expiry.tzinfo.utcoffset(expiry) is not None:
            # expiry is an "aware" datetime instance, meaning it has associated time zone information
            # ensure this datetime instance is expressed in UTC
            expiry = expiry.astimezone(timezone.utc)
        else:
            # expiry is a "naive" datetime instance, meaning it has no associated time zone information
            # assume this datetime instance was provided in UTC
            expiry = expiry.replace(tzinfo=timezone.utc)
        # now expiry is an "aware" datetime instance in UTC, format and add to the payload
        # datetime.isoformat() adds the UTC offset like +00:00
        # so keep everything but the last 6 characters and add the Z offset character
        return f"{expiry.isoformat(timespec='seconds')[:-6]}Z"

    def concession_groups_endpoint(self, group_id: str = None, *parts: str) -> str:
        """Endpoint for concession groups. Optionally provide a group_id for a group-specific endpoint."""
        return self._make_endpoint(self.CONCESSION_GROUPS, group_id, *parts)

    def concession_group_funding_source_endpoint(self, group_id: str, funding_source_id: str = None) -> str:
        """Endpoint for a concession group's funding sources."""
        return self.concession_groups_endpoint(group_id, FundingSourcesMixin.FUNDING_SOURCES, funding_source_id)

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

    def migrate_concession_group(self, group_id) -> dict:
        """Migrates a group from the old Customer Group format to current format."""
        endpoint = self.concession_groups_endpoint(group_id, "migrate")
        return self._post(endpoint, None, dict)

    def get_concession_group_linked_funding_sources(self, group_id) -> Generator[GroupFundingSourceResponse, None, None]:
        """Yield GroupFundingSourceResponse objects representing linked funding sources from the concession_groups endpoint."""
        endpoint = self.concession_group_funding_source_endpoint(group_id)
        for item in self._get_list(endpoint):
            yield GroupFundingSourceResponse(**item)

    def link_concession_group_funding_source(self, group_id: str, funding_source_id: str, expiry: datetime = None) -> dict:
        """Link a funding source to a concession group."""
        endpoint = self.concession_group_funding_source_endpoint(group_id)
        data = {"id": funding_source_id}

        if expiry is not None:
            data["expiry"] = self._format_expiry(expiry)

        return self._post(endpoint, data, dict)

    def update_concession_group_funding_source_expiry(self, group_id: str, funding_source_id: str, expiry: datetime) -> dict:
        """Update the expiry of a funding source already linked to a concession group."""
        endpoint = self.concession_group_funding_source_endpoint(group_id, funding_source_id)
        data = {"expiry": self._format_expiry(expiry)}

        return self._put(endpoint, data, dict)
