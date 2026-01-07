import abc

import pydantic

from ..notifications import Notification


class MutableModel(pydantic.BaseModel):
    """
    Base Pydantic model for all mutable models in `nwb2bids`.

    Parameters
    ----------
    _file_paths : list of str
        Private attribute to store file paths associated with this model.
        Used by the message feature to associate particular issues with particular files.
    """

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )


class BaseMetadataModel(MutableModel):
    """
    Base Pydantic model for all metadata handled by `nwb2bids`.
    """

    notifications: list[Notification] = pydantic.Field(
        description="List of auto-detected notifications.",
        default_factory=list,
        exclude=True,
    )


class BaseMetadataContainerModel(MutableModel, abc.ABC):
    """
    Base Pydantic model for 'containing' some number of other metadata models plus any extra metadata.
    """

    _internal_notifications: list[Notification] = pydantic.PrivateAttr(default_factory=list)

    @abc.abstractmethod
    @pydantic.computed_field
    @property
    def notifications(self) -> list[Notification]:
        """
        All notifications from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        message = "This field should be defined in child classes."
        raise NotImplementedError(message)
