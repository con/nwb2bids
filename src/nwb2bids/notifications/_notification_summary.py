import collections
import importlib.metadata
import json
import pathlib

from ._notification import Notification, _CustomJSONEncoder


def _get_nwb2bids_version() -> str:
    try:
        return importlib.metadata.version("nwb2bids")
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


def _group_notifications_by_identifier(notifications: list[Notification]) -> dict[str, list[Notification]]:
    """Group a list of notifications into an ordered dict keyed by identifier (or title)."""
    groups: dict[str, list[Notification]] = {}
    for n in notifications:
        key = n.identifier or n.title
        if key not in groups:
            groups[key] = []
        groups[key].append(n)
    return groups


def _merge_file_paths(group: list[Notification], attribute: str) -> list[str] | None:
    """Merge source or target file paths from all notifications in a group into a single deduplicated list."""
    merged = [str(p) for n in group for p in (getattr(n, attribute) or [])]
    return merged if merged else None


class NotificationSummary:
    """
    A structured, version-stamped summary of notifications from an nwb2bids inspection run.

    Provides human-readable text formatting, full JSON serialization, and file output
    for reviewing inspection results.

    Parameters
    ----------
    notifications : list of Notification
        The list of notifications to summarize.
    run_id : str, optional
        The run ID associated with this summary. Used for version-stamping the report.
    """

    def __init__(
        self,
        notifications: list[Notification],
        run_id: str | None = None,
    ) -> None:
        self.notifications = list(notifications)
        self.run_id = run_id
        self.nwb2bids_version = _get_nwb2bids_version()

    def __repr__(self) -> str:
        return (
            f"NotificationSummary("
            f"notifications={len(self.notifications)}, "
            f"run_id={self.run_id!r}, "
            f"nwb2bids_version={self.nwb2bids_version!r}"
            f")"
        )

    def __str__(self) -> str:
        """
        Human-readable aggregated text representation of the notification summary.

        Notifications of the same type (matched by ``identifier``) are grouped
        together with an occurrence count and a merged list of file paths, making
        this output suitable for printing in notebooks and IPython consoles.
        """
        return self._to_text(aggregate=True)

    def _to_text(self, aggregate: bool = True) -> str:
        """Build the text representation of this summary."""
        lines = []
        separator = "=" * 72
        section_separator = "-" * 72

        # Header
        lines.append(separator)
        lines.append("nwb2bids Inspection Report")
        lines.append(f"  nwb2bids version : {self.nwb2bids_version}")
        if self.run_id is not None:
            lines.append(f"  Run ID           : {self.run_id}")
        lines.append(separator)

        if not self.notifications:
            lines.append("")
            lines.append("No issues detected.")
            lines.append(separator)
            return "\n".join(lines)

        # Summary counts
        lines.append("")
        total = len(self.notifications)
        unique_types = len({n.identifier or n.title for n in self.notifications})
        lines.append(f"Found {total} notification(s) across {unique_types} unique type(s):")
        lines.append("")

        # Per-severity breakdown
        severity_counts = collections.Counter(n.severity.name for n in self.notifications)
        for severity_name in ("CRITICAL", "ERROR", "WARNING", "HINT", "INFO"):
            count = severity_counts.get(severity_name, 0)
            if count > 0:
                lines.append(f"  {severity_name}: {count}")
        lines.append("")

        if aggregate:
            # Group notifications by identifier and write one block per type
            for group in _group_notifications_by_identifier(self.notifications).values():
                representative = group[0]
                count = len(group)
                occurrence_label = "occurrence" if count == 1 else "occurrences"
                lines.append(section_separator)
                lines.append(
                    f"[{representative.severity.name} | {representative.category.name}] "
                    f"{representative.title} ({count} {occurrence_label})"
                )
                if representative.field is not None:
                    lines.append(f"  Field    : {representative.field}")
                if representative.data_standards:
                    standards = ", ".join(ds.name for ds in representative.data_standards)
                    lines.append(f"  Standards: {standards}")
                lines.append(f"  Reason   : {representative.reason}")
                lines.append(f"  Solution : {representative.solution}")
                if representative.examples:
                    lines.append("  Examples :")
                    for example in representative.examples:
                        lines.append(f"    {example}")

                all_source_paths = _merge_file_paths(group, "source_file_paths")
                all_target_paths = _merge_file_paths(group, "target_file_paths")
                if all_source_paths:
                    lines.append("  Source files:")
                    for path in all_source_paths:
                        lines.append(f"    {path}")
                if all_target_paths:
                    lines.append("  Target files:")
                    for path in all_target_paths:
                        lines.append(f"    {path}")
        else:
            # Write every individual notification as its own block
            for n in self.notifications:
                lines.append(section_separator)
                lines.append(f"[{n.severity.name} | {n.category.name}] {n.title}")
                if n.field is not None:
                    lines.append(f"  Field    : {n.field}")
                if n.data_standards:
                    standards = ", ".join(ds.name for ds in n.data_standards)
                    lines.append(f"  Standards: {standards}")
                lines.append(f"  Reason   : {n.reason}")
                lines.append(f"  Solution : {n.solution}")
                if n.examples:
                    lines.append("  Examples :")
                    for example in n.examples:
                        lines.append(f"    {example}")
                all_source_paths = _merge_file_paths([n], "source_file_paths")
                all_target_paths = _merge_file_paths([n], "target_file_paths")
                if all_source_paths:
                    lines.append("  Source files:")
                    for path in all_source_paths:
                        lines.append(f"    {path}")
                if all_target_paths:
                    lines.append("  Target files:")
                    for path in all_target_paths:
                        lines.append(f"    {path}")

        lines.append(separator)
        return "\n".join(lines)

    def to_json(self) -> str:
        """
        Return a JSON string with the full notification summary.

        All individual notifications are included without aggregation. The returned
        object contains the ``nwb2bids_version``, ``run_id``, and a ``notifications``
        list.
        """
        data = {
            "nwb2bids_version": self.nwb2bids_version,
            "run_id": self.run_id,
            "notifications": [n.model_dump(mode="json") for n in self.notifications],
        }
        return json.dumps(obj=data, indent=2, cls=_CustomJSONEncoder)

    def to_file(self, path: pathlib.Path, aggregate: bool = True) -> None:
        """
        Write the notification summary to a file.

        Parameters
        ----------
        path : pathlib.Path
            The path to the output file. When the file suffix is ``.json``, the output
            is written as structured JSON. Otherwise, the output is written as
            human-readable text.
        aggregate : bool, default: True
            When ``True``, notifications of the same type (matched by ``identifier``)
            are aggregated into a single entry that includes an occurrence count and a
            merged list of source and target file paths.  When ``False``, every
            individual notification is written as its own entry.
        """
        if path.suffix == ".json":
            if not aggregate:
                path.write_text(data=self.to_json())
            else:
                aggregated_notifications = []
                for group in _group_notifications_by_identifier(self.notifications).values():
                    entry = group[0].model_dump(mode="json")
                    entry["count"] = len(group)
                    entry["source_file_paths"] = _merge_file_paths(group, "source_file_paths")
                    entry["target_file_paths"] = _merge_file_paths(group, "target_file_paths")
                    aggregated_notifications.append(entry)

                data = {
                    "nwb2bids_version": self.nwb2bids_version,
                    "run_id": self.run_id,
                    "notifications": aggregated_notifications,
                }
                path.write_text(data=json.dumps(obj=data, indent=2, cls=_CustomJSONEncoder))
        else:
            path.write_text(data=self._to_text(aggregate=aggregate))

