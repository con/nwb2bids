# import json
# import os
# import pathlib
# import shutil
#
# import pydantic
# import pynwb
#
# from ._events import _get_events_metadata, _get_events_table
# from ._utils import _write_tsv
#
#
# @pydantic.validate_call
# def convert_nwb_dataset(
#     *,
#     nwb_directory: pydantic.DirectoryPath,
#     bids_directory: str | pathlib.Path,
#     copy: bool = True,
#     additional_metadata_file_path: pydantic.FilePath | None = None,
# ) -> None:
#     # electrodes, probes, and channels
#
#     for nwbfile_path, metadata in all_metadata.items():
#         participant_id = metadata["subject"]["participant_id"]
#         session_id = metadata["session"]["session_id"] or ""  # Follow-up TODO: cleanup the missing session ID case
#
#         print(participant_id, session_id)
#         if session_id:
#             os.makedirs(os.path.join(bids_directory, participant_id, session_id), exist_ok=True)
#         else:
#             os.makedirs(os.path.join(bids_directory, participant_id), exist_ok=True)
#         # Ephys might need to be dynamically selected, nwb can also be ieeg.
#         os.makedirs(os.path.join(bids_directory, participant_id, session_id, "ephys"), exist_ok=True)
#
#         # Temporary hack to get this to obey validation
#         file_prefix = (
#             f"{metadata['subject']['participant_id']}_{metadata['session']['session_id']}"
#             if metadata["session"].get("session_id", None) is not None
#             else f"{metadata['subject']['participant_id']}"
#         )
#         for var in ("electrodes", "probes", "channels"):
#             var_metadata = metadata[var]
#             # var_metadata = drop_false_keys(var_metadata)
#             var_metadata_file_path = os.path.join(
#                 bids_directory,
#                 participant_id,
#                 session_id,
#                 "ephys",
#                 f"{file_prefix}_{var}.tsv",
#             )
#             _write_tsv(var_metadata, var_metadata_file_path)
#
#         # Write events.tsv file
#         with pynwb.NWBHDF5IO(path=nwbfile_path, mode="r") as file_stream:
#             nwbfile = file_stream.read()
#
#             nwb_events_table = _get_events_table(nwbfile=nwbfile)
#
#         if nwb_events_table is not None:
#             # Collapse 'start_time' and 'stop_time' columns into 'onset' and 'duration' columns
#             bids_event_table = nwb_events_table.copy()
#             bids_event_table["duration"] = bids_event_table["stop_time"] - bids_event_table["start_time"]
#             bids_event_table = bids_event_table.rename(columns={"start_time": "onset"})
#             bids_event_table = bids_event_table.drop(columns=["stop_time"])
#             bids_event_table = bids_event_table.sort_values(
#                 by=["onset", "duration"], ascending=[True, False]
#             ).reset_index(drop=True)
#
#             # BIDS Validator is strict regarding column order
#             required_column_order = ["onset", "duration", "nwb_table"]
#             all_columns = list(bids_event_table.columns)
#             final_column_order = required_column_order + [
#                 column for column in all_columns if column not in required_column_order
#             ]
#
#             session_events_table_file_path = (
#                 bids_directory / participant_id / session_id / "ephys" / f"{file_prefix}_events.tsv"
#             )
#             bids_event_table.to_csv(
#                 path_or_buf=session_events_table_file_path,
#                 sep="\t",
#                 index=False,
#                 columns=final_column_order,
#             )
#
#             # Write events.json file
#             bids_event_metadata = _get_events_metadata(nwbfile=nwbfile)
#             additional_metadata_events = (
#                 additional_metadata.events.model_dump() if additional_metadata is not None else None or dict()
#             )
#             for key, value in additional_metadata_events.items():
#                 if key not in bids_event_metadata:
#                     bids_event_metadata[key] = value
#                 else:
#                     bids_event_metadata[key].update(value)
#
#             session_events_metadata_file_path = (
#                 bids_directory / participant_id / session_id / "ephys" / f"{file_prefix}_events.json"
#             )
#             with session_events_metadata_file_path.open(mode="w") as file_stream:
#                 json.dump(obj=bids_event_metadata, fp=file_stream, indent=4)
#
#         # Follow-up TODO: check events.json files, see if all are the same
#         # and if so remove the duplicates and move to outer level
#
#         # Rename and/or copy NWB file
#
#         bids_path = os.path.join(bids_directory, participant_id)
#         if metadata["session"]["session_id"]:
#             bids_path = os.path.join(bids_path, session_id)
#         bids_path = os.path.join(bids_directory, participant_id)
#
#         bids_path = os.path.join(
#             bids_directory,
#             metadata["subject"]["participant_id"],
#             session_id,
#             "ephys",
#             f"{file_prefix}_ephys.nwb",
#         )
#         if copy is True:
#             shutil.copyfile(src=nwb_file, dst=bids_path)
#         else:
#             open(bids_path, "a").close()
