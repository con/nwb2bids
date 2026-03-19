"""Utilities for looking up probe information from the ProbeInterface library."""

_PROBEINTERFACE_LIBRARY_BASE_URL = (
    "https://raw.githubusercontent.com/SpikeInterface/probeinterface_library/refs/heads/main"
)


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
    return f"{_PROBEINTERFACE_LIBRARY_BASE_URL}/{manufacturer}/{model}/{model}.json"
