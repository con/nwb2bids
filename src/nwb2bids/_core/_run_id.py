import datetime


def _generate_run_id() -> str:
    """
    Generate a unique run ID based on the current date and time.

    Returns
    -------
    run_id : str
        On each unique run of nwb2bids, a run ID is generated.
        Set this option to override this to any identifying string.
        This ID is used in the naming of the notification and sanitization reports saved to your cache directory.
        The default ID uses runtime timestamp information of the form "date-%Y%m%d_time-%H%M%S."
    """
    run_id = datetime.datetime.now().strftime("date-%Y%m%d_time-%H%M%S")
    return run_id
