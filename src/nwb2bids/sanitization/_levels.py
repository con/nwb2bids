import enum


class SanitizationLevel(enum.IntEnum):
    """
    The different levels of sanitization that can be applied to the `nwb2bids` conversion process.

    Attributes
    ----------
    NONE : int
        No sanitization is applied.
        This may result in invalid BIDS datasets.
    CRITICAL_BIDS_LABELS : int
        Only critical BIDS labels are sanitized.
        This primarily includes the session and subject labels,
        where any non-alphanumeric characters are replaced with plus signs.

    Examples
    --------
    A file such as `nwbfile.subject.subject_id = "My Subject_01"` becomes the `sub-My+Subject+01` entity-label pair
    in BIDS filenames when using the first level of sanitization.
    Otherwise, the filenames would have included the string `sub-My Subject_01`.
    """

    NONE = 0
    CRITICAL_BIDS_LABELS = 1
