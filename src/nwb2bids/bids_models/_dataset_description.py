import json
import typing

import pydantic
import typing_extensions


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

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @classmethod
    @pydantic.validate_call
    def from_file_path(cls, file_path: pydantic.FilePath) -> typing_extensions.Self | None:
        """
        Load the BIDS dataset description from a JSON file.

        Parameters
        ----------
        file_path : FilePath
            Path to the JSON file containing the dataset metadata.

        Returns
        -------
        BidsDatasetMetadata or None
            An instance of DatasetDescription populated with data from the file.
        """
        with file_path.open(mode="r") as file_stream:
            dictionary = json.load(fp=file_stream)

        dataset_description_content = dictionary.get("dataset_description", None)
        if dataset_description_content is None:
            return None

        dataset_metadata = cls(**dataset_description_content)
        return dataset_metadata
