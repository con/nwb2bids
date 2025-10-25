import pathlib


def _get_home_directory() -> pathlib.Path:
    """
    Get the home directory used by the `nwb2bids` project.

    Only light-weight configuration files are kept here.
    Heavier contents (such as text files, logs, etc.) are stored in the cache directory.
    """
    user_home = pathlib.Path.home()
    nwb2bids_home = user_home / ".nwb2bids"
    nwb2bids_home.mkdir(exist_ok=True)
    return nwb2bids_home
