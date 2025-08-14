import abc
import json
import pathlib
import shutil
import tempfile
import typing

import pydantic


class BaseConverter(pydantic.BaseModel, abc.ABC):

    @abc.abstractmethod
    def extract_metadata(self) -> None:
        """
        Extract essential metadata used by the BIDS standard from the source NWB files.
        """
        message = f"The `extract_metadata` method has not been implemented by the `{self.__class__.__name__}` class."
        raise NotImplementedError(message)

    def _handle_bids_directory(self, bids_directory: str | pathlib.Path | None = None) -> pathlib.Path:
        """
        Handle the BIDS directory path.

        If the directory does not exist, create it.
        If it exists, validate that it is a valid BIDS dataset.
        """
        if bids_directory is None:
            bids_directory = pathlib.Path.cwd()
        bids_directory = pathlib.Path(bids_directory)

        if bids_directory.exists():
            self._validate_existing_directory_as_bids(bids_directory=bids_directory)
        else:
            bids_directory.mkdir(exist_ok=True)
        self.extract_metadata()

        return bids_directory

    def _validate_existing_directory_as_bids(self, bids_directory: pathlib.Path) -> None:
        """
        Validate that the existing directory is a valid BIDS dataset.

        Parameters
        ----------
        bids_directory : pathlib.Path
            The path to the directory to validate.
        """
        dataset_description_file_path = bids_directory / "dataset_description.json"
        if len(list(bids_directory.iterdir())) == 0:
            default_dataset_description = {
                "BIDSVersion": "1.10",
            }
            with dataset_description_file_path.open(mode="w") as file_stream:
                json.dump(obj=default_dataset_description, fp=file_stream, indent=4)
            return

        if not dataset_description_file_path.exists():
            message = (
                f"The directory ({bids_directory}) exists and is not empty, but is not a valid BIDS dataset: "
                "missing 'dataset_description.json'."
            )
            raise ValueError(message)

        with dataset_description_file_path.open(mode="r") as file_stream:
            dataset_description = json.load(fp=file_stream)
        if dataset_description.get("BIDSVersion", None) is None:
            message = (
                f"The directory ({bids_directory}) exists but is not a valid BIDS dataset: "
                "missing 'BIDSVersion' in 'dataset_description.json'."
            )
            raise ValueError(message)

    @staticmethod
    def _handle_file_mode(
        file_mode: typing.Literal["move", "copy", "symlink", "auto"] = "auto",
    ) -> typing.Literal["move", "copy", "symlink"]:
        if file_mode != "auto":
            return file_mode

        try:
            test_directory = pathlib.Path(tempfile.mkdtemp(prefix="nwb2bids-"))
            test_file_path = test_directory / "test_file.txt"
            test_file_path.touch()
            (test_directory / "test_symlink.txt").symlink_to(target=test_file_path)
            shutil.rmtree(path=test_directory, ignore_errors=True)
            return "symlink"
        except (OSError, PermissionError):  # Windows can sometimes have trouble with symlinks
            return "copy"
