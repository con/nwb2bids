import typing

import pydantic


class _DatasetDescription(pydantic.BaseModel):
    """
    Schema for the dataset description in BIDS format.
    """

    Name: str = pydantic.Field(description="Name of the dataset.")
    BIDSVersion: str | None = pydantic.Field(
        description="The version of the BIDS standard that was used.",
        pattern=r"^\d+\.\d+(?:\.\d+)?$",
    )
    Description: str | None = pydantic.Field(
        description="Description of the dataset.",
        default=None,
    )
    DatasetType: typing.Literal["raw", "derivative"] | None = pydantic.Field(
        description="The interpretation of the dataset.",
        default=None,
    )
    Authors: list[str] | None = pydantic.Field(
        description="List of individuals who contributed to the creation/curation of the dataset.",
        default=None,
    )
    License: typing.Literal["CC-BY-4.0", "CC0-1.0"] | None = pydantic.Field(
        description="License under which the dataset is released.",
        default=None,
    )


class BidsDatasetMetadata(pydantic.BaseModel):
    """
    Schema for the metadata of a BIDS dataset.
    """

    dataset_description: _DatasetDescription = pydantic.Field(
        description="Dataset description including name, BIDS version, and other relevant information."
    )
