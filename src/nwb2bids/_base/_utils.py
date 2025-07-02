import csv
import pathlib

import pynwb


def _get_session_id_from_nwbfile_path(nwbfile_path: pathlib.Path) -> str:
    """
    Extract the session ID from the NWB file path.

    Parameters
    ----------
    nwbfile_path : str or pathlib.Path
        The path to the NWB file.

    Returns
    -------
    str
        The session ID extracted from the file path.
    """
    nwbfile = pynwb.read_nwb(nwbfile_path)
    return nwbfile.session_id


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
