"""Utilities for looking up probe information from the ProbeInterface library."""


def _get_probeinterface_term_url(*, manufacturer: str, model: str) -> str:
    """
    Construct the TermURL for a probe in the ProbeInterface library.

    Parameters
    ----------
    manufacturer : str
        The probe manufacturer name as used in the ProbeInterface library (e.g., 'neuronexus').
    model : str
        The probe model name as used in the ProbeInterface library (e.g., 'A1x32-Poly3-10mm-50-177').

    Returns
    -------
    term_url : str
        The raw URL pointing to the ProbeInterface JSON file in the library.
    """
    return (
        f"https://raw.githubusercontent.com/SpikeInterface/probeinterface_library"
        f"/refs/heads/main/{manufacturer}/{model}/{model}.json"
    )


def _parse_probe_flag(probe_flag: str) -> tuple[str, str]:
    """
    Parse a ``--probe`` CLI flag value into a (manufacturer, model) pair.

    The expected format is ``manufacturer/model``, e.g. ``neuronexus/A1x32-Poly3-10mm-50-177``.

    Parameters
    ----------
    probe_flag : str
        The value passed to the ``--probe`` CLI option.

    Returns
    -------
    manufacturer : str
        The manufacturer portion of the probe ID.
    model : str
        The model portion of the probe ID.

    Raises
    ------
    ValueError
        If ``probe_flag`` does not contain exactly one ``/`` separator.
    """
    parts = probe_flag.split("/", maxsplit=1)
    if len(parts) != 2 or not parts[0] or not parts[1]:
        message = (
            f"Invalid --probe value {probe_flag!r}. "
            "Expected format is 'manufacturer/model', e.g. 'neuronexus/A1x32-Poly3-10mm-50-177'."
        )
        raise ValueError(message)
    return parts[0], parts[1]
