import pydantic


class BaseMetadataModel(pydantic.BaseModel):
    """
    Base Pydantic model for all metadata handled by `nwb2bids`.
    """

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )
