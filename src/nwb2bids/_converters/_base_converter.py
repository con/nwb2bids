import abc

import pydantic

from ._run_config import RunConfig


class BaseConverter(pydantic.BaseModel, abc.ABC):
    run_config: RunConfig = pydantic.Field(
        description="The configuration for this conversion run.", default_factory=RunConfig
    )

    @abc.abstractmethod
    def extract_metadata(self) -> None:
        """
        Extract essential metadata used by the BIDS standard from the source NWB files.
        """
        message = f"The `extract_metadata` method has not been implemented by the `{self.__class__.__name__}` class."
        raise NotImplementedError(message)
