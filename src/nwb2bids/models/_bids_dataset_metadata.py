import json
import typing

import pydantic

from ._bids_session_metadata import BidsSessionMetadata


class DatasetDescription(pydantic.BaseModel):
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

    dataset_description: DatasetDescription | None = pydantic.Field(
        description="Dataset description including name, BIDS version, and other relevant information.",
        default=None,
    )
    sessions_metadata: list[BidsSessionMetadata] = pydantic.Field(
        description="Metadata collected from all sessions in the dataset.",
        min_length=1,
    )

    @classmethod
    @pydantic.validate_call
    def from_file_path(cls, file_path: pydantic.FilePath) -> typing.Self:
        """
        Load BIDS dataset metadata from a JSON file.

        Parameters
        ----------
        file_path : FilePath
            Path to the JSON file containing the dataset metadata.

        Returns
        -------
        BidsDatasetMetadata
            An instance of BidsDatasetMetadata populated with data from the file.
        """
        with file_path.open(mode="r") as file_stream:
            dictionary = json.load(fp=file_stream)
        return cls(**dictionary)
