import json
import pathlib
import typing

import pandas
import pydantic
import pynwb
import typing_extensions

from ..bids_models._base_metadata_model import BaseMetadataModel


class Events(BaseMetadataModel):
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
    _bids_events_data_frame: pandas.DataFrame = pydantic.PrivateAttr()
    _nwbfiles: list[pynwb.NWBFile] = pydantic.PrivateAttr()

    @classmethod
    @pydantic.validate_call
    def from_nwbfiles(cls, nwbfiles: list[pydantic.InstanceOf[pynwb.NWBFile]]) -> typing_extensions.Self | None:
        """
        Extracts all events from the in-memory NWBFile objects.

        Supports both core NWB ``TimeIntervals`` tables (trials, epochs, custom time intervals) and
        ndx-events neurodata types (``EventsTable`` from ndx-events v0.4.0+, as well as ``Events``,
        ``LabeledEvents``, ``AnnotatedEventsTable``, and ``TTLs`` from older ndx-events versions).

        Future improvements will include support for DynamicTables with ``*_time`` columns.
        """
        if len(nwbfiles) > 1:
            message = "Conversion of multiple NWB files per session is not yet supported."
            raise NotImplementedError(message)
        nwbfile = nwbfiles[0]

        bids_events_data_frame = _get_events_data_frame(nwbfile=nwbfile)
        if bids_events_data_frame is None:
            return None

        bids_events_data_frame = bids_events_data_frame.sort_values(
            by=["onset", "duration"], ascending=[True, False], na_position="last"
        ).reset_index(drop=True)

        dictionary: dict[str, typing.Any] = {
            "onset": bids_events_data_frame["onset"].tolist(),
            "duration": bids_events_data_frame["duration"].tolist(),
        }
        custom_fields = set(bids_events_data_frame.columns) - {"onset", "duration"}
        dictionary.update({custom_field: list(bids_events_data_frame[custom_field]) for custom_field in custom_fields})

        bids_events = cls(**dictionary)
        bids_events._bids_events_data_frame = bids_events_data_frame
        bids_events._nwbfiles = nwbfiles
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
        if getattr(self, "_bids_events_data_frame", None) is None:
            message = (
                "Writing to TSV is only supported for Events instances created via `.from_nwbfiles` "
                "(missing internal data frame). If you would like to request support for direct instantiation, please "
                "raise an issue at https://github.com/con/nwb2bids/issues/new."
            )
            raise NotImplementedError(message)

        required_column_order = ["onset", "duration", "nwb_table"]
        column_order = required_column_order + [
            column for column in self._bids_events_data_frame.columns if column not in required_column_order
        ]

        self._bids_events_data_frame.to_csv(
            path_or_buf=file_path, sep="\t", index=False, columns=column_order, na_rep="n/a"
        )

    @pydantic.validate_call
    def to_json(self, file_path: str | pathlib.Path) -> None:
        """
        Write the BIDS events JSON sidecar file.

        Parameters
        ----------
        file_path : str or pathlib.Path
            The path to the output JSON file.
        """
        if getattr(self, "_bids_events_data_frame", None) is None:
            message = (
                "Writing to JSON is only supported for Events instances created via `.from_nwbfiles` "
                "(missing internal file reference). If you would like to request support for direct instantiation, "
                "please raise an issue at https://github.com/con/nwb2bids/issues/new."
            )
            raise NotImplementedError(message)
        file_path = pathlib.Path(file_path)

        fields_metadata = _get_events_metadata(nwbfile=self._nwbfiles[0])

        with file_path.open(mode="w") as file_stream:
            json.dump(obj=fields_metadata, fp=file_stream, indent=4)


_NDX_EVENTS_CLASS_NAMES = frozenset(
    {
        # ndx-events v0.4.0+: redesigned DynamicTable-based API
        "EventsTable",
        # ndx-events v1.x: simple timestamped events
        "Events",
        # ndx-events v2.x: added label and TTL support
        "LabeledEvents",
        "AnnotatedEventsTable",
        "TTLs",
    }
)
"""Class names (as strings) associated with ndx-events neurodata types across known versions."""


def _get_all_time_intervals(
    nwbfile: pynwb.NWBFile,
) -> list[pynwb.epoch.TimeIntervals] | None:
    """
    Extracts all time interval events from the NWB file and returns them as a list of TimeIntervals objects.
    """
    time_intervals: list[pynwb.epoch.TimeIntervals] = [
        neurodata_object
        for neurodata_object in nwbfile.objects.values()
        if isinstance(neurodata_object, pynwb.epoch.TimeIntervals)
    ]

    if len(time_intervals) == 0:
        return None

    return time_intervals


def _get_all_ndx_events_tables(nwbfile: pynwb.NWBFile) -> list[typing.Any] | None:
    """
    Find all ndx-events neurodata objects in the NWB file.

    Detection is done by class name string to avoid a hard dependency on any specific version of the
    ndx-events extension.  The following class names are recognised across known versions:

    * ``EventsTable``         – ndx-events v0.4.0+
    * ``Events``              – ndx-events v1.x / v2.x
    * ``LabeledEvents``       – ndx-events v2.x
    * ``AnnotatedEventsTable``– ndx-events v2.x
    * ``TTLs``                – ndx-events v2.x
    """
    ndx_events_tables = [
        neurodata_object
        for neurodata_object in nwbfile.objects.values()
        if type(neurodata_object).__name__ in _NDX_EVENTS_CLASS_NAMES
    ]

    if len(ndx_events_tables) == 0:
        return None

    return ndx_events_tables


def _get_columns_to_skip(
    time_intervals: list[pynwb.epoch.TimeIntervals], default_exclusion: set[str] | None = None
) -> set[str]:
    """
    Retrieve a set of column names to exclude.

    Current exclusions primarily include indexed columns.
    This will automatically include `timeseries` columns since they are indexed.
    """
    skip_columns = set() if default_exclusion is None else default_exclusion.copy()
    true_column_names = {
        column.name for time_interval in time_intervals for column in time_interval.columns
    }  # PyNWB keeps hiding info otherwise

    for column_name in true_column_names:
        if (indexed_column_name := f"{column_name}_index") in true_column_names:
            skip_columns.add(column_name)
            skip_columns.add(indexed_column_name)

    return skip_columns


def _ndx_events_table_to_data_frame(neurodata_object: typing.Any) -> pandas.DataFrame | None:
    """
    Convert a single ndx-events neurodata object to a pandas DataFrame with ``onset`` and ``duration`` columns.

    The conversion is written to be version-agnostic:

    * **EventsTable** (ndx-events v0.4.0+) – uses ``to_dataframe()`` and renames the ``timestamp``
      column to ``onset``.  If a ``duration`` column is present its values are used directly
      (NaN entries remain NaN so they are written as ``n/a`` in the BIDS TSV); otherwise all
      ``duration`` values are set to ``float("nan")``.

    * **Events / LabeledEvents / AnnotatedEventsTable / TTLs** (older versions) – reads the
      ``timestamps`` attribute if present, or falls back to ``data`` for TTL-style objects.
      Durations default to ``float("nan")``.  Any ``labels`` attribute is preserved as an
      additional column.
    """
    class_name = type(neurodata_object).__name__

    if class_name == "EventsTable":
        # v0.4.0+: built as a DynamicTable; timestamp column is always present.
        df = neurodata_object.to_dataframe().reset_index(drop=True)

        # Rename the required timestamp column to onset
        if "timestamp" in df.columns:
            df = df.rename(columns={"timestamp": "onset"})
        else:
            return None

        # Ensure a duration column exists (NaN where unavailable)
        if "duration" not in df.columns:
            df["duration"] = float("nan")

        return df

    # Older ndx-events versions (v1/v2): Events, LabeledEvents, AnnotatedEventsTable, TTLs
    timestamps = getattr(neurodata_object, "timestamps", None)
    if timestamps is None:
        # TTLs-style objects store pulse data in a 'data' attribute rather than 'timestamps'
        timestamps = getattr(neurodata_object, "data", None)
    if timestamps is None:
        return None

    df = pandas.DataFrame({"onset": list(timestamps), "duration": float("nan")})

    # Preserve optional label columns present in older versions
    for attr_name in ("labels", "label"):
        labels = getattr(neurodata_object, attr_name, None)
        if labels is not None:
            df[attr_name] = list(labels)

    return df


def _get_events_data_frame(nwbfile: pynwb.NWBFile) -> pandas.DataFrame | None:
    """
    Extracts all events (TimeIntervals and ndx-events) from the NWB file and returns them as a single
    data frame with unified ``onset`` and ``duration`` columns.

    TimeIntervals ``start_time`` and ``stop_time`` columns are converted to ``onset`` and ``duration``
    respectively.  ndx-events tables already provide an ``onset`` column (from their ``timestamp``
    column) and an optional ``duration`` column (``float("nan")`` where unavailable).

    A ``nwb_table`` column is added to every row to identify the source table.
    """
    time_intervals = _get_all_time_intervals(nwbfile=nwbfile)
    ndx_events_tables = _get_all_ndx_events_tables(nwbfile=nwbfile)

    if time_intervals is None and ndx_events_tables is None:
        return None

    all_table_names: list[str] = []
    all_data_frames: list[pandas.DataFrame] = []

    if time_intervals is not None:
        time_interval_names = [time_interval.name for time_interval in time_intervals]
        if len(set(time_interval_names)) != len(time_interval_names):
            message = (
                f"\nFound duplicate time interval names in the NWB file: {time_interval_names}\n"
                "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
            )
            raise ValueError(message)
        all_table_names.extend(time_interval_names)

        all_column_names = {
            column_name: True for time_interval in time_intervals for column_name in time_interval.colnames
        }
        if all_column_names.get("nwb_table", None) is not None:
            message = (
                "\nA column with the name 'nwb_table' was found in the NWB file.\n"
                "This is reserved for the nwb2bids conversion process and will require an override to proceed.\n"
                "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
            )
            raise ValueError(message)

        # Exclude timeseries and indexed columns - note that the sister `_index` columns are excluded by
        # `.to_dataframe()`
        skip_columns = _get_columns_to_skip(time_intervals=time_intervals)
        ti_frames = [time_interval.to_dataframe(exclude=skip_columns) for time_interval in time_intervals]
        for index, time_interval in enumerate(time_intervals):
            # Convert start_time/stop_time → onset/duration
            ti_frames[index]["duration"] = ti_frames[index]["stop_time"] - ti_frames[index]["start_time"]
            ti_frames[index] = ti_frames[index].rename(columns={"start_time": "onset"})
            ti_frames[index] = ti_frames[index].drop(columns=["stop_time"])
            ti_frames[index]["nwb_table"] = time_interval.name
        all_data_frames.extend(ti_frames)

    if ndx_events_tables is not None:
        ndx_events_names = [obj.name for obj in ndx_events_tables]
        if len(set(ndx_events_names)) != len(ndx_events_names):
            message = (
                f"\nFound duplicate ndx-events table names in the NWB file: {ndx_events_names}\n"
                "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
            )
            raise ValueError(message)

        for ndx_events_table in ndx_events_tables:
            df = _ndx_events_table_to_data_frame(neurodata_object=ndx_events_table)
            if df is None:
                continue
            df["nwb_table"] = ndx_events_table.name
            all_data_frames.append(df)
            all_table_names.append(ndx_events_table.name)

    if len(all_data_frames) == 0:
        return None

    if len(set(all_table_names)) != len(all_table_names):
        duplicates = [name for name in all_table_names if all_table_names.count(name) > 1]
        message = (
            f"\nFound duplicate table names across TimeIntervals and ndx-events in the NWB file: {duplicates}\n"
            "Please raise an issue at https://github.com/con/nwb2bids/issues/new.\n\n"
        )
        raise ValueError(message)

    events_table = pandas.concat(objs=all_data_frames, ignore_index=True)
    return events_table


def _get_default_hed_tag(table_name: str, time_intervals: list[pynwb.epoch.TimeIntervals] | None) -> str:
    """
    Return the default HED tag for a table that is not in the common mapping.

    TimeIntervals-sourced tables get ``"Time-interval"`` (matching the original behaviour for
    custom interval tables).  ndx-events-sourced tables get ``"Sensory-event"``.
    """
    if time_intervals is not None:
        time_interval_names = {ti.name for ti in time_intervals}
        if table_name in time_interval_names:
            return "Time-interval"
    return "Sensory-event"


def _get_events_metadata(nwbfile: pynwb.NWBFile) -> dict | None:
    time_intervals = _get_all_time_intervals(nwbfile=nwbfile)
    ndx_events_tables = _get_all_ndx_events_tables(nwbfile=nwbfile)

    if time_intervals is None and ndx_events_tables is None:
        return None

    common_nwb_table_hed = {
        "trials": "Experimental-trial",
        "epochs": "Time-block",
    }

    event_metadata: dict[str, typing.Any] = {
        "onset": {"Description": "Onset of the event, measured from the beginning of the acquisition.", "Units": "s"},
        "duration": {"Description": "Duration of the event (measured from onset).", "Units": "s"},
    }

    all_table_names: list[str] = []

    if time_intervals is not None:
        time_interval_names = [time_interval.name for time_interval in time_intervals]
        all_table_names.extend(time_interval_names)

        skip_columns = _get_columns_to_skip(
            time_intervals=time_intervals, default_exclusion={"start_time", "stop_time"}
        )
        for time_interval in time_intervals:
            cols_to_write = [column for column in time_interval.columns if column.name not in skip_columns]
            for column in cols_to_write:
                event_metadata[column.name] = {"Description": column.description}

    if ndx_events_tables is not None:
        ndx_events_names = [obj.name for obj in ndx_events_tables]
        all_table_names.extend(ndx_events_names)

        for ndx_events_table in ndx_events_tables:
            # Collect non-onset/duration columns for JSON sidecar
            colnames = getattr(ndx_events_table, "colnames", ())
            skip_cols = {"timestamp", "duration"}
            for col_name in colnames:
                if col_name in skip_cols:
                    continue
                # Try to get the description from the column object
                col_obj = ndx_events_table.get(col_name) if hasattr(ndx_events_table, "get") else None
                if col_obj is None:
                    col_obj = getattr(ndx_events_table, col_name, None)
                description = getattr(col_obj, "description", col_name) if col_obj is not None else col_name
                if col_name not in event_metadata:
                    event_metadata[col_name] = {"Description": description}

    event_metadata["nwb_table"] = {
        "Description": "The name of the NWB table from which this event was extracted.",
        "Levels": {table_name: f"The '{table_name}' table in the NWB file." for table_name in all_table_names},
        "HED": {
            table_name: common_nwb_table_hed.get(table_name, _get_default_hed_tag(table_name, time_intervals))
            for table_name in all_table_names
        },
    }

    # Descriptions for TimeIntervals tables (nested under their names)
    if time_intervals is not None:
        event_metadata.update(
            {
                time_interval.name: {"Description": time_interval.description}
                for time_interval in time_intervals
                if time_interval.description
            }
        )

    # Descriptions for ndx-events tables (nested under their names)
    if ndx_events_tables is not None:
        for ndx_events_table in ndx_events_tables:
            description = getattr(ndx_events_table, "description", None)
            if description:
                event_metadata[ndx_events_table.name] = {"Description": description}

    return event_metadata
