import pydantic

from .._messages._inspection_message import InspectionMessage


class BaseMetadataModel(pydantic.BaseModel):
    """
    Base Pydantic model for all metadata handled by `nwb2bids`.
    """

    messages: list[InspectionMessage] = pydantic.Field(
        description="List of auto-detected suggestions.",
        default_factory=list,
    )
    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )


class BaseMetadataContainerModel(pydantic.BaseModel):
    """
    Base Pydantic model for 'containing' some number of other metadata models plus any extra metadata.
    """

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @pydantic.computed_field
    @property
    def messages(self) -> list[InspectionMessage]:
        """
        All messages from contained session converters.

        These can accumulate over time based on which instance methods have been called.
        """
        message = "This field should be defined in child classes."
        raise NotImplementedError(message=message)
