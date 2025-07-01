import json
import os
import pathlib
import shutil

import pydantic
import pynwb

from ._additional_metadata import _load_and_validate_additional_metadata, _write_dataset_description
from ._events import _get_events_metadata, _get_events_table
from ._utils import _extract_metadata, _write_tsv
from ._write_info import _write_sessions_info, _write_subjects_info


@pydantic.validate_call
def convert_nwb_dataset(
    *,
    nwb_directory: pydantic.DirectoryPath,
    bids_directory: str | pathlib.Path,
    copy: bool = True,
    additional_metadata_file_path: pydantic.FilePath | None = None,
) -> None:
    """
    Convert a directory of NWB files to BIDS format.

    Parameters
    ----------
    nwb_directory : directory path
        The path to the directory containing NWB files.
    bids_directory : directory path
        The path to the directory where the BIDS dataset will be created.
    copy : bool
        Whether to copy the NWB files into the BIDS dataset directory.
        The default is True.
    additional_metadata_file_path : file path, optional
        The path to a JSON file containing additional metadata to be included in the BIDS dataset.
        If not provided, the function will also look for a file named "additional_metadata.json" in the NWB directory.
    """
    bids_directory = pathlib.Path(bids_directory)
    bids_directory.mkdir(exist_ok=True)
    additional_metadata_file_path = (
        secondary_path
        if additional_metadata_file_path is None
        and (secondary_path := pathlib.Path(nwb_directory) / "additional_metadata.json").exists()
        else additional_metadata_file_path
    )

    additional_metadata = None
    if additional_metadata_file_path is not None:
        additional_metadata = _load_and_validate_additional_metadata(file_path=additional_metadata_file_path)
        _write_dataset_description(additional_metadata=additional_metadata, bids_directory=bids_directory)

    nwb_files = list(nwb_directory.rglob(pattern="*.nwb"))
    all_metadata = dict()
    for nwb_file in nwb_files:
        all_metadata[nwb_file] = _extract_metadata(nwb_file)

    _write_subjects_info(all_metadata=all_metadata, bids_directory=bids_directory)

    # TODO: fix metadata passing here
    _write_sessions_info(subjects=all_metadata, bids_directory=bids_directory)

    # electrodes, probes, and channels

    for nwbfile_path, metadata in all_metadata.items():
        participant_id = metadata["subject"]["participant_id"]
        session_id = metadata["session"]["session_id"] or ""  # Follow-up TODO: cleanup the missing session ID case

        print(participant_id, session_id)
        if session_id:
            os.makedirs(os.path.join(bids_directory, participant_id, session_id), exist_ok=True)
        else:
            os.makedirs(os.path.join(bids_directory, participant_id), exist_ok=True)
        # Ephys might need to be dynamically selected, nwb can also be ieeg.
        os.makedirs(os.path.join(bids_directory, participant_id, session_id, "ephys"), exist_ok=True)

        # Temporary hack to get this to obey validation
        file_prefix = (
            f"{metadata['subject']['participant_id']}_{metadata['session']['session_id']}"
            if metadata["session"].get("session_id", None) is not None
            else f"{metadata['subject']['participant_id']}"
        )
        for var in ("electrodes", "probes", "channels"):
            var_metadata = metadata[var]
            # var_metadata = drop_false_keys(var_metadata)
            var_metadata_file_path = os.path.join(
                bids_directory,
                participant_id,
                session_id,
                "ephys",
                f"{file_prefix}_{var}.tsv",
            )
            _write_tsv(var_metadata, var_metadata_file_path)

        # Write events.tsv file
        with pynwb.NWBHDF5IO(path=nwbfile_path, mode="r") as file_stream:
            nwbfile = file_stream.read()

            nwb_events_table = _get_events_table(nwbfile=nwbfile)

        if nwb_events_table is not None:
            # Collapse 'start_time' and 'stop_time' columns into 'onset' and 'duration' columns
            bids_event_table = nwb_events_table.copy()
            bids_event_table["duration"] = bids_event_table["stop_time"] - bids_event_table["start_time"]
            bids_event_table = bids_event_table.rename(columns={"start_time": "onset"})
            bids_event_table = bids_event_table.drop(columns=["stop_time"])
            bids_event_table = bids_event_table.sort_values(
                by=["onset", "duration"], ascending=[True, False]
            ).reset_index(drop=True)

            # BIDS Validator is strict regarding column order
            required_column_order = ["onset", "duration", "nwb_table"]
            all_columns = list(bids_event_table.columns)
            final_column_order = required_column_order + [
                column for column in all_columns if column not in required_column_order
            ]

            session_events_table_file_path = (
                bids_directory / participant_id / session_id / "ephys" / f"{file_prefix}_events.tsv"
            )
            bids_event_table.to_csv(
                path_or_buf=session_events_table_file_path,
                sep="\t",
                index=False,
                columns=final_column_order,
            )

            # Write events.json file
            bids_event_metadata = _get_events_metadata(nwbfile=nwbfile)
            additional_metadata_events = (
                additional_metadata.events.model_dump() if additional_metadata is not None else None or dict()
            )
            for key, value in additional_metadata_events.items():
                if key not in bids_event_metadata:
                    bids_event_metadata[key] = value
                else:
                    bids_event_metadata[key].update(value)

            session_events_metadata_file_path = (
                bids_directory / participant_id / session_id / "ephys" / f"{file_prefix}_events.json"
            )
            with session_events_metadata_file_path.open(mode="w") as file_stream:
                json.dump(obj=bids_event_metadata, fp=file_stream, indent=4)

        # Follow-up TODO: check events.json files, see if all are the same
        # and if so remove the duplicates and move to outer level

        # Rename and/or copy NWB file

        bids_path = os.path.join(bids_directory, participant_id)
        if metadata["session"]["session_id"]:
            bids_path = os.path.join(bids_path, session_id)
        bids_path = os.path.join(bids_directory, participant_id)

        bids_path = os.path.join(
            bids_directory,
            metadata["subject"]["participant_id"],
            session_id,
            "ephys",
            f"{file_prefix}_ephys.nwb",
        )
        if copy is True:
            shutil.copyfile(src=nwb_file, dst=bids_path)
        else:
            open(bids_path, "a").close()
