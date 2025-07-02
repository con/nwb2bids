import json
import os
import pathlib

from ._utils import _drop_false_keys, _write_tsv
from ..models import BidsDatasetMetadata


def _write_dataset_description(*, bids_dataset_metadata: BidsDatasetMetadata, bids_directory: pathlib.Path) -> None:
    file_path = bids_directory / "dataset_description.json"
    content = bids_dataset_metadata.dataset_description.model_dump_json(indent=4)
    file_path.write_text(data=content)


def _write_sessions_info(
    subjects,
    bids_directory: pathlib.Path,
    all_metadata: dict,
):
    default_session_json = {
        "session_quality": {
            "LongName": "General quality of the session",
            "Description": "Quality of the session",
            "Levels": {
                "Bad": "Bad quality, should not be considered for further analysis",
                "ok": "Ok quality, can be considered for further analysis with care",
                "good": "Good quality, should be used for analysis",
                "Excellent": "Excellent quality, extraordinarily good session",
            },
        },
        "data_quality": {
            "LongName": "Quality of the recorded signals",
            "Description": "Quality of the recorded signals",
            "Levels": {
                "Bad": "Bad quality, should not be considered for further analysis",
                "ok": "Ok quality, can be considered for further analysis with care",
                "good": "Good quality, should be used for analysis",
                "Excellent": "Excellent quality, extraordinarily good session",
            },
        },
        "number_of_trials": {
            "LongName": "Number of trials in this session",
            "Description": "Count of attempted trials in the session (integer)",
        },
        "comment": {
            "LongName": "General comments",
            "Description": "General comments by the experimenter on the session",
        },
    }

    for subject in subjects:
        participant_id = subject["participant_id"]

        os.makedirs(os.path.join(bids_directory, participant_id), exist_ok=True)

        for metadata in all_metadata.values():
            sessions = [x["session"] for x in all_metadata.values() if x["subject"]["participant_id"] == participant_id]

            sessions = _drop_false_keys(sessions)

            sessions_file_path = os.path.join(bids_directory, participant_id, f"{participant_id}_sessions.tsv")
            sessions_keys = _write_tsv(sessions, sessions_file_path)
            sessions_keys = {}
            sessions_json = {k: v for k, v in default_session_json.items() if k in sessions_keys}

            with open(
                os.path.join(bids_directory, participant_id, f"{participant_id}_sessions.json"),
                "w",
            ) as json_file:
                json.dump(sessions_json, json_file, indent=4)
