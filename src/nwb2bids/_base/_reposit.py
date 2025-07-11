import warnings

from ._convert_nwb_dataset import convert_nwb_dataset


def reposit(
    in_dir: str, out_dir: str, *, no_copy: bool = False, additional_metadata_file_path: str | None = None
) -> None:
    message = (
        "The `nwb2bids.reposit` function is deprecated and will be removed in a future release. "
        "Please use `nwb2bids.convert_nwb_dataset` instead.",
    )
    warnings.warn(message=message, category=DeprecationWarning, stacklevel=2)

    convert_nwb_dataset(
        nwb_directory=in_dir,
        out_dir=out_dir,
        file_mode="move" if no_copy is True else "copy",
        additional_metadata_file_path=additional_metadata_file_path,
    )
