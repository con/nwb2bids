import json

import pydantic

from ._bids_session_metadata import BidsSessionMetadata
from ._dataset_description import DatasetDescription


class BidsDatasetMetadata(pydantic.BaseModel):
    """
    Schema for the metadata of a BIDS dataset.
    """

    dataset_description: DatasetDescription | None = pydantic.Field(
        description="Dataset description including name, BIDS version, and other relevant information.",
        default=None,
    )
    sessions_metadata: list[BidsSessionMetadata] | None = pydantic.Field(
        description="Metadata collected from all sessions in the dataset.",
        min_length=1,
        default=None,
    )

    @pydantic.model_validator(mode="after")
    def check_at_least_one_value(self) -> "BidsDatasetMetadata":
        if self.dataset_description is None and self.sessions_metadata is None:
            message = "Please set either `dataset_description` or `sessions_metadata` to instantiate this class."
            raise ValueError(message)
        return self

    @classmethod
    @pydantic.validate_call
    def from_file_path(cls, file_path: pydantic.FilePath) -> "BidsDatasetMetadata":
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

        dataset_metadata = cls(**dictionary)
        return dataset_metadata

    def update(self, other: "BidsDatasetMetadata") -> "BidsDatasetMetadata":
        # TODO: could add sophisticated logic for handling merges/updates
        if self.dataset_description is None and other.dataset_description is not None:
            self.dataset_description = other.dataset_description
        elif self.dataset_description is not None and other.dataset_description is not None:
            message = (
                "Combining two `BidsDatasetMetadata` classes that both possess a `dataset_description` "
                "field has not yet been implemented."
            )
            raise NotImplementedError(message)

        if self.sessions_metadata is None and other.sessions_metadata is not None:
            self.sessions_metadata = other.sessions_metadata
        elif self.sessions_metadata is not None and other.sessions_metadata is not None:
            message = (
                "Combining two `BidsDatasetMetadata` classes that both possess a `sessions_metadata` "
                "field has not yet been implemented."
            )
            raise NotImplementedError(message)

        return self
