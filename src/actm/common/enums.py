"""Enumeration classes for ACTM."""

from enum import Enum
from typing import Optional


class ACTMEnum(Enum):
    """Base class for ACTM enumerations (name = value)."""

    def __init__(self, eid: str, description: str = ""):
        self._id = eid
        self._description = description

    @property
    def id(self):
        """Get the id of the enumeration."""
        return self._id

    @property
    def description(self):
        """Get the description of the enumeration."""
        return self._description

    def __str__(self):
        if self._description:
            return f"{self.id} - {self.description}"
        return self.id

    @classmethod
    def from_id(cls, eid: str) -> Optional["ACTMEnum"]:
        """Get the enumeration from the given id."""
        return next((enum for enum in cls if enum.id == eid), None)

    @classmethod
    def from_name(cls, name: str) -> Optional["ACTMEnum"]:
        """Get the enumeration from the given name."""
        return next((enum for enum in cls if enum.name == name), None)

    @classmethod
    def ids(cls) -> list[str]:
        """Get the ids for the enumeration."""
        return [enum.id for enum in cls]

    @classmethod
    def list(cls):
        """Get the list of the enumeration."""
        return list(cls)


class SupportedEnum(ACTMEnum):
    """Base class for supported enumerations."""

    def __init__(self, eid: str, is_supported: bool, description: str = ""):
        super().__init__(eid, description)
        self._is_supported = is_supported

    def __str__(self):
        return f"{self.id} - {self.description} (Supported: {self.is_supported})"

    @property
    def is_supported(self):
        """Check if the enumeration is supported."""
        return self._is_supported

    @classmethod
    def supported_ids(cls):
        """Get the supported ids for the enumeration."""
        return [enum.id for enum in cls if enum.is_supported]


class DownloadType(SupportedEnum):
    """Enumeration for download types."""

    ACTIVITIES = ("activities", True)
    FACILITY_RENTALS = ("facility-rentals", False)
    DROP_IN_PROGRAMS = ("drop-in-programs", False)
    MEMBERSHIPS = ("memberships", False)


class DataSaveFormat(ACTMEnum):
    """Enumeration for data save formats."""

    TEXT = ("text", "Text file")
    CSV = ("csv", "CSV file")
    JSON = ("json", "JSON file")
