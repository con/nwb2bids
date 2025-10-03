import enum


class SanitizationLevel(enum.IntEnum):
    """
    The different levels of sanitization that can be applied to the `nwb2bids` conversion process.

    Parameters
    ----------
    NONE : int
        No sanitization is applied.
        This may result in invalid BIDS datasets.
    CRITICAL_BIDS_LABELS : int
        Only critical BIDS labels are sanitized.
        This primarily includes the session and subject labels,
        where any non-alphanumeric characters are replaced with plus signs.

        For example: `nwbfile.subject = My-Subject_01` becomes `sub-My+Subject+01` entity in BIDS filenames.
    """

    NONE = 0
    CRITICAL_BIDS_LABELS = 1
