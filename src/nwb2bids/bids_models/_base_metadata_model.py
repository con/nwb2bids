import abc

import pydantic

from .._inspection._inspection_result import InspectionResult


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

    messages: list[InspectionResult] = pydantic.Field(
        description="List of auto-detected suggestions.",
        default_factory=list,
    )

    def model_dump(self, **kwargs) -> dict:
        model_dump = super().model_dump(
            exclude={
                "messages": ...,
                **{k: {"messages": ...} for k, v in self.__dict__.items() if isinstance(v, pydantic.BaseModel)},
            },
            **kwargs,
        )
        return model_dump


class BaseMetadataContainerModel(MutableModel, abc.ABC):
    """
    Base Pydantic model for 'containing' some number of other metadata models plus any extra metadata.
    """

    @abc.abstractmethod
    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionResult]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        message = "This field should be defined in child classes."
        raise NotImplementedError(message=message)
