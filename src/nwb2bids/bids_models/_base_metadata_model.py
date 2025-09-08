import pydantic

from .._messages import InspectionMessage


class BaseMetadataModel(pydantic.BaseModel):
    """
    Base Pydantic model for all metadata handled by `nwb2bids`.
    """

    messages: list[InspectionMessage] = pydantic.Field(
        description="List of auto-detected suggestions.", ge=0, default_factory=list
    )
    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )
