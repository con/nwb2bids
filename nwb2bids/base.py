from pynwb import NWBHDF5IO
from pynwb.ecephys import ElectricalSeries
from pathlib import Path
import os
import csv
import json
import shutil
import re


# The star is required by clize to know to typeset it as `--no-copy` instead of `no-copy`.
def reposit(
    in_dir,
    out_dir,
    *,
    no_copy=False,
    additional_metadata_file_path: str | Path | None = None,
):

    in_dir = os.path.abspath(os.path.expanduser(in_dir))
    out_dir = os.path.abspath(os.path.expanduser(out_dir))

    if additional_metadata_file_path is not None:
        additional_metadata_file_path = Path(additional_metadata_file_path)
    elif (
        secondary_path := Path(in_dir) / "additional_metadata.json"
    ).exists():  # Try to find it in_dir
        additional_metadata_file_path = secondary_path

    all_metadata = {}
    additional_metadata = {}
    if additional_metadata_file_path is not None:
        # TODO: add validation of additional metadata schema
        with additional_metadata_file_path.open(mode="r") as file_stream:
            additional_metadata = json.load(fp=file_stream)

    # Top-level fields (required for BIDS)
    # TODO: determine how many fields in this are required (such as DOI) vs. chicken and egg of upload to DANDI
    # Possible that DANDI itself should be primarily responsible for modifying certain things at time of publication
    dataset_description = additional_metadata["dataset_description"]
    dataset_description_file_path = os.path.join(out_dir, "dataset_description.json")
    with open(file=dataset_description_file_path, mode="r") as file_stream:
        json.dump(obj=dataset_description, fp=file_stream)

    # Fields within NWB files
    nwb_files = list(Path(in_dir).rglob("*.[nN][wW][bB]"))

    for nwb_file in nwb_files:
        metadata = extract_metadata(nwb_file)
        all_metadata[nwb_file] = extract_metadata(nwb_file)

    os.makedirs(out_dir, exist_ok=True)

    subjects = unique_list_of_dicts([x["subject"] for x in all_metadata.values()])

    subjects = drop_false_keys(subjects)

    subjects_file_path = os.path.join(out_dir, "participants.tsv")
    subjects_keys = write_tsv(subjects, subjects_file_path)

    # create particiants JSON
    default_subjects_json = {
        "subject_id": {"Description": "Unique identifier of the subject"},
        "species": {"Description": "The binomial species name from the NCBI Taxonomy"},
        "strain": {"Description": "Identifier of the strain"},
        "birthdate": {
            "Description": "Day of birth of the participant in ISO8601 format"
        },
        "age": {
            "Description": "Age of the participant at time of recording",
            "Units": "days",
        },
        "sex": {"Description": "Sex of participant"},
    }

    subjects_json = {
        k: v for k, v in default_subjects_json.items() if k in subjects_keys
    }
    with open(os.path.join(out_dir, "participants.json"), "w") as json_file:
        json.dump(subjects_json, json_file, indent=4)

    # sessions

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

        os.makedirs(os.path.join(out_dir, participant_id), exist_ok=True)

        for metadata in all_metadata.values():
            sessions = [
                x["session"]
                for x in all_metadata.values()
                if x["subject"]["participant_id"] == participant_id
            ]

            sessions = drop_false_keys(sessions)

            sessions_file_path = os.path.join(out_dir, participant_id, "sessions.tsv")
            sessions_keys = write_tsv(sessions, sessions_file_path)
            sessions_json = {
                k: v for k, v in default_session_json.items() if k in sessions_keys
            }

            with open(
                os.path.join(out_dir, participant_id, "sessions.json"), "w"
            ) as json_file:
                json.dump(sessions_json, json_file, indent=4)

    # contacts, probes, and channels

    for metadata in all_metadata.values():
        participant_id = metadata["subject"]["participant_id"]
        session_id = metadata["session"]["session_id"]
        print(participant_id, session_id)

        if session_id:
            os.makedirs(
                os.path.join(out_dir, participant_id, session_id), exist_ok=True
            )
        else:
            os.makedirs(os.path.join(out_dir, participant_id), exist_ok=True)
        # Ephys might need to be dynamically selected, nwb can also be ieeg.
        os.makedirs(
            os.path.join(out_dir, participant_id, session_id, "ephys"), exist_ok=True
        )

        for var in ("contacts", "probes", "channels"):
            var_metadata = metadata[var]
            var_metadata = drop_false_keys(var_metadata)
            var_metadata_file_path = os.path.join(
                out_dir,
                participant_id,
                session_id,
                "ephys",
                f"{participant_id}_{var}.tsv",
            )
            write_tsv(var_metadata, var_metadata_file_path)

        bids_path = os.path.join(out_dir, participant_id)
        if metadata["session"]["session_id"]:
            bids_path = os.path.join(bids_path, session_id)
        bids_path = os.path.join(out_dir, participant_id)

        bids_path = os.path.join(
            out_dir,
            metadata["subject"]["participant_id"],
            metadata["session"]["session_id"],
            "ephys",
            f"{metadata['subject']['participant_id']}_{metadata['session']['session_id']}_ephys.nwb",
        )
        if no_copy:
            open(bids_path, "a").close()
        else:
            shutil.copyfile(nwb_file, bids_path)


def sanitize_bids_value(in_string, pattern=r"[^a-zA-Z0-9]", replacement="X"):
    out_string = re.sub(pattern, replacement, in_string)
    return out_string


def extract_metadata(filepath: str) -> dict:

    with NWBHDF5IO(filepath, load_namespaces=True) as io:
        nwbfile = io.read()

        subject = nwbfile.subject

        # Should we except this?
        # Right now excepting because of testdata constraints
        try:
            probes = set([x.device for x in nwbfile.electrodes["group"][:]])
            contacts = nwbfile.electrodes
        except TypeError:
            probes = []
            contacts = []

        ess = [x for x in nwbfile.objects.values() if isinstance(x, ElectricalSeries)]

        metadata = {
            "general_ephys": {
                "InstitutionName": nwbfile.institution,
            },
            "subject": {
                "participant_id": "sub-" + sanitize_bids_value(subject.subject_id),
                "species": subject.species,
                "strain": subject.strain,
                "birthday": subject.date_of_birth,
                "age": subject.age,
                "sex": subject.sex,
            },
            "session": {
                "session_id": (
                    "ses-" + sanitize_bids_value(nwbfile.session_id)
                    if nwbfile.session_id
                    else ""
                ),
                "number_of_trials": len(nwbfile.trials) if nwbfile.trials else None,
                "comments": nwbfile.session_description,
            },
            "probes": [
                {
                    "probe_id": probe.name,
                    "type": "unknown",
                    "description": probe.description,
                    "manufacturer": probe.manufacturer,
                }
                for probe in probes
            ],
            "contacts": [
                {
                    "contact_id": contact.index[0],
                    "probe_id": contact.group.iloc[0].device.name,
                    # TODO "impedance": contact["imp"].iloc[0] if contact["imp"].iloc[0] > 0 else None,
                    "location": (
                        contact["location"].iloc[0]
                        if contact["location"].iloc[0] not in ("unknown",)
                        else None
                    ),
                }
                for contact in contacts
            ],
            "channels": [
                {
                    "channel_id": contact.index[0],
                    "contact_id": contact.index[0],
                    "type": "EXT",
                    "unit": "V",
                    "sampling_frequency": ess[0].rate,
                    "gain": ess[0].conversion,
                }
                for contact in contacts
            ],
        }
    return metadata


def unique_list_of_dicts(data):
    # Convert to set of tuples
    unique_data = set(tuple(d.items()) for d in data)
    # Convert back to list of dictionaries
    unique_list_of_dicts = [dict(t) for t in unique_data]
    return unique_list_of_dicts


def drop_false_keys(list_of_dict):
    list_of_dict = [{k: v for k, v in d.items() if v} for d in list_of_dict]
    return list_of_dict


def write_tsv(list_of_dict, file_path):
    """
    Write a list of dictionaries to a tsv file using all keys as columns.

    Notes
    -----
    1. The order of columns should maybe be tweaked.
    """

    keys = set().union(*(d.keys() for d in list_of_dict))
    with open(file_path, "w") as f:
        dict_writer = csv.DictWriter(
            f,
            keys,
            delimiter="\t",
        )
        dict_writer.writeheader()
        dict_writer.writerows(list_of_dict)
    return keys


# Actually copy the NWB files
