import pydantic


class SanitizationConfig(pydantic.BaseModel):
    """
    The different types of sanitization that can be applied to the `nwb2bids` conversion process.

    Not enabling many of these options may lead to the creation of an invalid BIDS dataset.

    Attributes
    ----------
    sub_labels : bool, default: False
        Subject labels are sanitized by replacing any non-alphanumeric characters with plus signs.
    ses_labels : bool, default: False
        Session labels are sanitized by replacing any non-alphanumeric characters with plus signs.

    Examples
    --------
    A file such as `nwbfile.subject.subject_id = "My Subject_01"` becomes the `sub-My+Subject+01` entity-label pair
    in BIDS filenames when using `SUB_LABELS = True`.
    Otherwise, the filenames would have included the string `sub-My Subject_01`.
    """

    sub_labels: bool = False
    ses_labels: bool = False

    model_config = pydantic.ConfigDict(
        frozen=True,  # Make the model immutable
        validate_default=True,  # Validate default values as well
    )
