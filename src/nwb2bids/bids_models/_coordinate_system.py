import json
import pathlib
import typing

_COORDINATE_SYSTEM_DATA: dict[str, dict[str, str]] = {
    "AllenCCFv3": {
        "MicroephysCoordinateSystem": "AllenCCFv3",
        "MicroephysCoordinateUnits": "um",
        "MicroephysCoordinateSystemDescription": (
            "Allen Mouse Brain Common Coordinate Framework version 3. "
            "The origin is at the anterior commissure. "
            "X is anterior-posterior (anterior positive), "
            "Y is inferior-superior (superior positive), "
            "Z is left-right (right positive). "
            "Coordinates are in micrometers."
        ),
        "MicroephysCoordinateProcessingDescription": (
            "Electrode positions were registered to the Allen CCF using anatomical landmarks "
            "and/or histological verification."
        ),
        "MicroephysCoordinateProcessingReference": "https://doi.org/10.1016/j.cell.2020.04.007",
    },
    "PaxinosWatson": {
        "MicroephysCoordinateSystem": "PaxinosWatson",
        "MicroephysCoordinateUnits": "mm",
        "MicroephysCoordinateSystemDescription": (
            "Paxinos and Watson Rat Brain Atlas, 7th edition. "
            "The origin is at Bregma. "
            "X is anterior-posterior (anterior positive), "
            "Y is inferior-superior (superior positive), "
            "Z is left-right (right positive). "
            "Coordinates are in millimeters."
        ),
        "MicroephysCoordinateProcessingDescription": (
            "Electrode positions were registered to the Paxinos and Watson atlas using anatomical landmarks "
            "and/or histological verification."
        ),
        "MicroephysCoordinateProcessingReference": "https://doi.org/10.1016/C2009-0-63235-9",
    },
}


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
    space : str
        The space/atlas label (e.g., ``"AllenCCFv3"`` or ``"PaxinosWatson"``).
    """
    file_path = pathlib.Path(file_path)
    content = _COORDINATE_SYSTEM_DATA[space]
    with file_path.open(mode="w") as file_stream:
        json.dump(obj=content, fp=file_stream, indent=4)
