import pandas
import pynwb


def _get_all_time_intervals(
    nwbfile: pynwb.NWBFile,
) -> list[pynwb.epoch.TimeIntervals] | None:
    """
    Extracts all time interval events from the NWB file and returns them as a list of TimeIntervals objects.
    """
    time_intervals: list[pynwb.epoch.TimeIntervals] = [
        neurodata_object
        for neurodata_object in nwbfile.acquisition.values()
        if isinstance(neurodata_object, pynwb.epoch.TimeIntervals)
    ]
    if nwbfile.trials is not None:
        time_intervals.append(nwbfile.trials)
    if nwbfile.epochs is not None:
        time_intervals.append(nwbfile.epochs)

    if len(time_intervals) == 0:
        return None

    return time_intervals


def _get_events_table(nwbfile: pynwb.NWBFile) -> pandas.DataFrame | None:
    """
    Extracts all time interval events from the NWB file and returns them as a single data frame.

    Future improvements will include support for non-interval events (ndx-events) and DynamicTables with *_time columns.
    """
    time_intervals = _get_all_time_intervals(nwbfile=nwbfile)
    if time_intervals is None:
        return None

    time_interval_names = [time_interval.name for time_interval in time_intervals]
    if len(set(time_interval_names)) != len(time_interval_names):
        message = (
            f"\nFound duplicate time interval names in the NWB file: {time_interval_names}\n"
            "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
        )
        raise ValueError(message)

    all_column_names = {column_name: True for time_interval in time_intervals for column_name in time_interval.colnames}
    if all_column_names.get("nwb_table", None) is not None:
        message = (
            "\nA column with the name 'nwb_table' was found in the NWB file.\n"
            "This is reserved for the nwb2bids conversion process and will require an override to proceed.\n"
            "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
        )
        raise ValueError(message)

    all_data_frames = [time_interval.to_dataframe() for time_interval in time_intervals]
    for index, time_interval in enumerate(time_intervals):
        all_data_frames[index]["nwb_table"] = time_interval.name

    events_table = pandas.concat(objs=all_data_frames, ignore_index=True)
    return events_table


def _get_events_metadata(nwbfile: pynwb.NWBFile) -> dict | None:
    time_intervals = _get_all_time_intervals(nwbfile=nwbfile)
    if time_intervals is None:
        return None

    time_interval_names = [time_interval.name for time_interval in time_intervals]

    common_nwb_table_hed = {
        "trials": "Experimental-trial",
        "epochs": "Time-block",
    }

    event_metadata = {
        time_interval.name: {"Description": time_interval.description}
        for time_interval in time_intervals
        if time_interval.description
    }

    # Follow-up TODO: assign HED tags based on neurodata type once extended beyond TimeIntervals
    event_metadata["nwb_table"] = {
        "nwb_table": {
            "Description": "The name of the NWB table from which this event was extracted.",
            "Levels": {table_name: f"The '{table_name}' table in the NWB file." for table_name in time_interval_names},
            "HED": {
                table_name: common_nwb_table_hed.get(table_name, "Time-interval") for table_name in time_interval_names
            },
        }
    }

    return event_metadata
