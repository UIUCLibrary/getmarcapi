"""Retrieve records from the API.

This module is for managing the way records are requested from the api
"""

import abc
from typing import Mapping, Optional


class AbsRecordStrategy(abc.ABC):
    """Base class for working with various types of records."""

    def __init__(self, args: Mapping):
        """Working with various types of identifiers.

        Args:
            args:
                Args used by the incoming get request
        """
        self.args = args

    @abc.abstractmethod
    def get_record(self, server, identifier) -> str:
        """Retrieve a record for a given identifier."""

    @abc.abstractmethod
    def get_identifier(self, args: Mapping) -> str:
        """Parse the request arguments for the identifier."""


class Bibid(AbsRecordStrategy):
    """UIUC bibid used in old Voyager catalog."""

    def get_record(self, server, identifier) -> str:
        """Get the record for the bibid from the server.

        Args:
            server: Server used to make api request
            identifier: bibid of the record

        Returns:
            xml record for the bibid

        """
        return server.get_record(identifier, "bibid")

    def get_identifier(self, args: Mapping) -> str:
        """Retrieve the bibid from the args.

        Args:
            args:

        Returns:
            bibid

        """
        return args['bibid']


class RecordGetter:
    """Public class for interacting with records from the api record server."""

    def __init__(self, args: Mapping) -> None:
        """Interacting with records from the api record server.

        Args:
            args:
                Args used by the incoming get request
        """
        self._strategy = self._get_strategy(args)
        if self._strategy is None:
            raise ValueError(
                "args provided is unable to determine what type strategy"
            )

    def __str__(self) -> str:
        return \
            f"{self.__repr__()} {self._strategy.__class__.__name__} strategy"

    @staticmethod
    def _get_strategy(args: Mapping) -> Optional[AbsRecordStrategy]:
        # todo: _get_strategy
        if "bibid" in args:
            return Bibid(args)
        return None

    def get_record(self, server, identifier: str) -> str:
        """Retrieve a record for a given identifier.

        Args:
            identifier: Identifier used for a given record

        Returns:
            MARC xml record

        """
        assert self._strategy is not None  # nosec
        record = self._strategy.get_record(server, identifier)
        if record is None:
            raise ValueError(
                "Unable retrieve record for {}".format(identifier)
            )
        return record

    def get_identifier(self, args: Mapping) -> str:
        """Parse the request args for the identifier requested, regardless of its type.

        Args:
            args: request args

        Returns:
            identifier in the api request.

        """
        if self._strategy is None:
            raise TypeError("No valid strategy to get record")
        return self._strategy.get_identifier(args)
