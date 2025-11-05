import abc
import json
import pathlib
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

    @staticmethod
    def _validate_existing_directory_as_bids(bids_directory: pathlib.Path) -> None:
        """
        Validate that the existing directory is a valid BIDS dataset.

        Parameters
        ----------
        bids_directory : pathlib.Path
            The path to the directory to validate.
        """
        dataset_description_file_path = bids_directory / "dataset_description.json"

        current_directory_contents = {
            path.stem for path in bids_directory.iterdir() if not path.name.startswith(".")
        } - {"README", "CHANGES", "derivatives", "dandiset"}
        if len(current_directory_contents) == 0:
            # Import here to avoid circular import
            from ..bids_models import DatasetDescription

            # Create minimal dataset description using the model
            # model_post_init() will automatically add GeneratedBy
            minimal_dataset_description = DatasetDescription(
                Name=bids_directory.name if bids_directory.name else "BIDS dataset",
                BIDSVersion="1.10",
            )
            with dataset_description_file_path.open(mode="w") as file_stream:
                json.dump(obj=minimal_dataset_description.model_dump(), fp=file_stream, indent=4)
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

        with tempfile.TemporaryDirectory(prefix="nwb2bids-") as temp_dir_str:
            temp_dir_path = pathlib.Path(temp_dir_str)

            # Create a test file
            test_file_path = temp_dir_path / "test_file.txt"
            test_file_path.touch()

            try:
                # Create a symlink to the test file
                (temp_dir_path / "test_symlink.txt").symlink_to(target=test_file_path)
            except (OSError, PermissionError, NotImplementedError):  # Windows can sometimes have trouble with symlinks
                # TODO: log a INFO message here when logging is set up
                return "copy"
            else:
                # If symlink creation was successful, return "symlink"
                return "symlink"
