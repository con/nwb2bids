import csv
import re

import pynwb


def _sanitize_bids_value(in_string, pattern=r"[^a-zA-Z0-9]", replacement="X"):
    out_string = re.sub(pattern, replacement, in_string)
    return out_string


def _extract_metadata(filepath: str) -> dict:

    with pynwb.NWBHDF5IO(filepath, load_namespaces=True) as io:
        nwbfile = io.read()

        subject = nwbfile.subject

        # Should we except this?
        # Right now excepting because of testdata constraints
        try:
            probes = set([x.device for x in nwbfile.electrodes["group"][:]])
            electrodes = nwbfile.electrodes
        except TypeError:
            probes = []
            electrodes = []

        ess = [x for x in nwbfile.objects.values() if isinstance(x, pynwb.ecephys.ElectricalSeries)]

        metadata = {
            "general_ephys": {
                "InstitutionName": nwbfile.institution,
            },
            "subject": {
                "participant_id": "sub-" + _sanitize_bids_value(subject.subject_id),
                "species": subject.species,
                "strain": subject.strain,
                "birthday": subject.date_of_birth,
                "age": subject.age,
                "sex": subject.sex,
            },
            "session": {
                "session_id": ("ses-" + nwbfile.session_id if nwbfile.session_id else None),
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
            "electrodes": [
                {
                    "electrode_id": electrode.index[0],
                    "probe_id": electrode.group.iloc[0].device.name,
                    # TODO "impedance": electrode["imp"].iloc[0] if electrode["imp"].iloc[0] > 0 else None,
                    "location": (
                        electrode["location"].iloc[0] if electrode["location"].iloc[0] not in ("unknown",) else None
                    ),
                }
                for electrode in electrodes
            ],
            "channels": [
                {
                    "channel_id": electrode.index[0],
                    "electrode_id": electrode.index[0],
                    "type": "EXT",
                    "unit": "V",
                    "sampling_frequency": ess[0].rate,
                    "gain": ess[0].conversion,
                }
                for electrode in electrodes
            ],
        }
    return metadata


def _unique_list_of_dicts(data):
    # Convert to set of tuples
    unique_data = set(tuple(d.items()) for d in data)
    # Convert back to list of dictionaries
    unique_list_of_dicts = [dict(t) for t in unique_data]
    return unique_list_of_dicts


def _drop_false_keys(list_of_dict):
    list_of_dict = [{k: v for k, v in d.items() if v} for d in list_of_dict]
    return list_of_dict


def _write_tsv(list_of_dict, file_path):
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
