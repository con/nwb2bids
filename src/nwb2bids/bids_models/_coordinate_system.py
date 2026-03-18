"""
This submodule has been simplified from the style of its siblings.

Rather than defining a mutable Pydantic model with live validation, we encode a few hard-coded
JSON contents to directly lookup and dump when needed.
"""

import json
import pathlib
import typing


def write_coordsystem_json(
    file_path: str | pathlib.Path,
    space: typing.Literal["AllenCCFv3", "PaxinosWatson"],
) -> None:
    """
    Write a BIDS coordinate system JSON sidecar file for the given space label.

    Parameters
    ----------
    file_path : path
        The path to the output `*_coordsystem.json` file.
    space : {"AllenCCFv3", "PaxinosWatson"}
        The space/atlas label.
    """
    file_path = pathlib.Path(file_path)
    data_file_path = pathlib.Path(__file__).parent / "_coordinate_system_data.json"
    all_data: dict[str, dict[str, str]] = json.loads(data_file_path.read_text())
    content = all_data[space]
    with file_path.open(mode="w") as file_stream:
        json.dump(obj=content, fp=file_stream, indent=4)
