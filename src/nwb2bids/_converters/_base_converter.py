import abc
import typing

import pydantic

from ._run_config import RunConfig
from ..notifications import Notification


class BaseConverter(pydantic.BaseModel, abc.ABC):
    run_config: typing.Annotated[
        RunConfig, pydantic.Field(description="The configuration for this conversion run.", default_factory=RunConfig)
    ]
    _internal_notifications: list[Notification] = pydantic.PrivateAttr(default_factory=list)

    @abc.abstractmethod
    def extract_metadata(self) -> None:
        """
        Extract essential metadata used by the BIDS standard from the source NWB files.
        """
        message = f"The `extract_metadata` method has not been implemented by the `{self.__class__.__name__}` class."
        raise NotImplementedError(message)
