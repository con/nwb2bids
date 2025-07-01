import json
import os
import pathlib

from ._utils import _drop_false_keys, _unique_list_of_dicts, _write_tsv
from ..schemas import BidsDatasetMetadata


def _write_dataset_description(*, bids_dataset_metadata: BidsDatasetMetadata, bids_directory: pathlib.Path) -> None:
    file_path = bids_directory / "dataset_description.json"
    content = bids_dataset_metadata.dataset_description.model_dump_json(indent=4)
    file_path.write_text(data=content)


def _write_subjects_info(
    *,
    all_metadata: dict,
    bids_directory: pathlib.Path,
) -> None:
    subjects = _unique_list_of_dicts([x["subject"] for x in all_metadata.values()])

    subjects = _drop_false_keys(subjects)

    subjects_file_path = os.path.join(bids_directory, "participants.tsv")
    # BIDS validation enforces column order
    # Follow-up TODO: make keys dynamic based on availability
    # Follow-up TODO: generalize to more subjects
    possible_subject_fields = ["participant_id", "species", "strain", "sex"]
    subject_fields = [field for field in possible_subject_fields if subjects[0].get(field, None) is not None]
    subject_header = "\t".join(subject_fields)
    subject_lines = [f"{subject_header}\n"]
    for subject in subjects:
        line = "\t".join(subject[field] for field in subject_fields)
        subject_lines.append(f"{line}\n")

    # TSV writer below is hard to control header order - TSV is not hard to write directly, so just do it here...
    with open(file=subjects_file_path, mode="w") as file_stream:
        file_stream.writelines(subject_lines)

    # create participants JSON
    default_subjects_json = {
        "subject_id": {"Description": "Unique identifier of the subject"},
        "species": {"Description": "The binomial species name from the NCBI Taxonomy"},
        "strain": {"Description": "Identifier of the strain"},
        "birthdate": {"Description": "Day of birth of the participant in ISO8601 format"},
        "age": {
            "Description": "Age of the participant at time of recording",
            "Units": "days",
        },
        "sex": {"Description": "Sex of participant"},
    }

    subjects_json = {k: v for k, v in default_subjects_json.items() if k in subject_fields}
    with open(os.path.join(bids_directory, "participants.json"), "w") as json_file:
        json.dump(subjects_json, json_file, indent=4)


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
