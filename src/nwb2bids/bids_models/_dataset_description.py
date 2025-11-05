import importlib.metadata
import json
import typing

import pydantic
import typing_extensions

from ._base_metadata_model import BaseMetadataModel


class GeneratedByItem(BaseMetadataModel):
    """
    Schema for a single GeneratedBy entry in BIDS dataset_description.json.

    Represents provenance information about a pipeline or process that generated the dataset.
    """

    Name: str = pydantic.Field(
        description="Name of the pipeline or process that generated the outputs.",
    )
    Version: str = pydantic.Field(
        description="Version of the pipeline.",
    )
    Description: str = pydantic.Field(
        description="Plain-text description of the pipeline or process that generated the outputs.",
    )
    CodeURL: str = pydantic.Field(
        description="URL where the code used to generate the dataset may be found.",
    )


class GeneratedByNwb2bids(GeneratedByItem):
    """
    nwb2bids-specific GeneratedBy entry with defaults for the nwb2bids pipeline.
    """

    Name: str = pydantic.Field(default="nwb2bids")
    Version: str = pydantic.Field(default_factory=lambda: importlib.metadata.version(distribution_name="nwb2bids"))
    Description: str = pydantic.Field(default="Tool to reorganize NWB files into a BIDS directory layout.")
    CodeURL: str = pydantic.Field(default="https://github.com/con/nwb2bids")


class DatasetDescription(BaseMetadataModel):
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
    DatasetType: typing.Literal["raw", "derivative"] = pydantic.Field(
        description="The interpretation of the dataset.",
        default="raw",
    )
    Authors: list[str] | None = pydantic.Field(
        description="List of individuals who contributed to the creation/curation of the dataset.",
        default=None,
    )
    License: typing.Literal["CC-BY-4.0", "CC0-1.0"] | None = pydantic.Field(
        description="License under which the dataset is released.",
        default=None,
    )
    GeneratedBy: list[GeneratedByItem] | None = pydantic.Field(
        description="Provenance information - pipelines that generated this dataset.",
        default=None,
    )

    def model_post_init(self, context: typing.Any, /) -> None:
        generated_by_nwb2bids = GeneratedByNwb2bids()
        if self.GeneratedBy is None:
            self.GeneratedBy = [generated_by_nwb2bids]
        else:
            self.GeneratedBy.append(generated_by_nwb2bids)

    @pydantic.model_validator(mode="after")
    def validate_exactly_one_nwb2bids(self) -> typing_extensions.Self:
        if self.GeneratedBy is not None:
            nwb2bids_count = sum(1 for item in self.GeneratedBy if item.Name == "nwb2bids")
            if nwb2bids_count != 1:
                raise ValueError(f"GeneratedBy must contain exactly one nwb2bids entry, found {nwb2bids_count}")
        return self

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
