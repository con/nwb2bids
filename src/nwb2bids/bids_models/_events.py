import json
import pathlib

import pandas
import pydantic
import pynwb
import typing_extensions


class Events(pydantic.BaseModel):
    onset: list[float] = pydantic.Field(
        description=(
            "Onset (in seconds) of the event, measured from the beginning of the acquisition of the first data point "
            "stored in the corresponding task data file. Negative onsets are allowed, to account for events that occur "
            "prior to the first stored data point. For example, in case there is a training phase that "
            "begins before the scanning sequence has started, then events from this sequence should have negative "
            "onset time counting down to the beginning of the acquisition of the first recording. If any data "
            "points have been discarded before forming the data file, a time of 0 corresponds to the first stored "
            "data point and not the first acquired data point."
        )
    )
    duration: list[float] = pydantic.Field(
        description=(
            "Duration of the event (measured from onset) in seconds. Must always be either zero or positive "
            '(or n/a if unavailable). A "duration" value of zero implies that the delta function or event is so '
            "short as to be effectively modeled as an impulse."
        ),
    )
    _bids_events_data_frame: pandas.DataFrame
    _nwbfiles: list[pynwb.NWBFile]

    model_config = pydantic.ConfigDict(
        validate_assignment=True,  # Re-validate model on mutation
        extra="allow",  # Allow additional custom fields
    )

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        """
        Extracts all time interval events from the in-memory NWBFile objects.

        Future improvements will include support for non-interval events (ndx-events)
        and DynamicTables with *_time columns.
        """
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        nwbfile = nwbfiles[0]

        nwb_events_data_frame = _get_events_data_frame(nwbfile=nwbfile)
        if nwb_events_data_frame is None:
            return None

        # Collapse 'start_time' and 'stop_time' columns into 'onset' and 'duration' columns
        bids_events_data_frame = nwb_events_data_frame.copy()
        bids_events_data_frame["duration"] = bids_events_data_frame["stop_time"] - bids_events_data_frame["start_time"]
        bids_events_data_frame = bids_events_data_frame.rename(columns={"start_time": "onset"})
        bids_events_data_frame = bids_events_data_frame.drop(columns=["stop_time"])
        bids_events_data_frame = bids_events_data_frame.sort_values(
            by=["onset", "duration"], ascending=[True, False]
        ).reset_index(drop=True)

        dictionary = {
            "onset": bids_events_data_frame["onset"].tolist(),
            "duration": bids_events_data_frame["duration"].tolist(),
        }
        custom_fields = set(bids_events_data_frame.columns) - {"onset", "duration"}
        dictionary.update({custom_field: list(bids_events_data_frame[custom_field]) for custom_field in custom_fields})
        dictionary["_bids_events_data_frame"] = bids_events_data_frame
        dictionary["_nwbfiles"] = nwbfiles

        bids_events = cls(**dictionary)
        return bids_events

    @pydantic.validate_call
    def to_tsv(self, file_path: str | pathlib.Path) -> None:
        """
        Write the BIDS events table to a TSV file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            The path to the output TSV file.
        """
        bids_events_data_frame = self.model_extra["_bids_events_data_frame"]

        required_column_order = ["onset", "duration", "nwb_table"]
        column_order = required_column_order + [
            column for column in bids_events_data_frame.columns if column not in required_column_order
        ]

        bids_events_data_frame.to_csv(path_or_buf=file_path, sep="\t", index=False, columns=column_order)

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Write the BIDS events JSON sidecar file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            The path to the output JSON file.
        """
        nwbfile = self.model_extra["_nwbfiles"][0]

        fields_metadata = _get_events_metadata(nwbfile=nwbfile)

        with file_path.open(mode="w") as file_stream:
            json.dump(obj=fields_metadata, fp=file_stream, indent=4)


def _get_events_data_frame(nwbfile: pynwb.NWBFile) -> pandas.DataFrame | None:
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
