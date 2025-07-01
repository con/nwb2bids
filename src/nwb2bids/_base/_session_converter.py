import pathlib
import typing

import pydantic
import pynwb

from ._utils import _sanitize_bids_value
from ..schemas import BidsSessionMetadata


class SessionConverter(pydantic.BaseModel):
    def __init__(self, nwb_file_path: pydantic.FilePath) -> None:
        """
        Initialize a converter of NWB files to BIDS format.

        Parameters
        ----------
        nwb_directory : directory path
            The path to the directory containing NWB files.
        """
        super().__init__()

        self.nwb_file_path = pathlib.Path(nwb_file_path)
        self.session_metadata: BidsSessionMetadata | None = None

    def extract_session_metadata(self) -> BidsSessionMetadata:
        """
        Extract metadata from the NWB file across the specified directory.
        """
        with pynwb.NWBHDF5IO(path=self.nwb_file_path, load_namespaces=True) as file_stream:
            nwbfile = file_stream.read()

            subject = nwbfile.subject

            # Should we except this?
            # Right now excepting because of testdata constraints
            try:
                probes = set([x.device for x in nwbfile.electrodes["group"][:]])
                electrodes = nwbfile.electrodes
            except TypeError:
                probes = []
                electrodes = []

            ess = [x for x in nwbfile.objects.values() if isinstance(x, pynwb.ecephys.ElectricalSeries)]

            self.session_metadata = {
                "general_ephys": {
                    "InstitutionName": nwbfile.institution,
                },
                "subject": {
                    "participant_id": "sub-" + _sanitize_bids_value(subject.subject_id),
                    "species": subject.species,
                    "strain": subject.strain,
                    "birthday": subject.date_of_birth,
                    "age": subject.age,
                    "sex": subject.sex,
                },
                "session": {
                    "session_id": ("ses-" + nwbfile.session_id if nwbfile.session_id else None),
                    "number_of_trials": len(nwbfile.trials) if nwbfile.trials else None,
                    "comments": nwbfile.session_description,
                },
                "probes": [
                    {
                        "probe_id": probe.name,
                        "type": "unknown",
                        "description": probe.description,
                        "manufacturer": probe.manufacturer,
                    }
                    for probe in probes
                ],
                "electrodes": [
                    {
                        "electrode_id": electrode.index[0],
                        "probe_id": electrode.group.iloc[0].device.name,
                        # TODO "impedance": electrode["imp"].iloc[0] if electrode["imp"].iloc[0] > 0 else None,
                        "location": (
                            electrode["location"].iloc[0] if electrode["location"].iloc[0] not in ("unknown",) else None
                        ),
                    }
                    for electrode in electrodes
                ],
                "channels": [
                    {
                        "channel_id": electrode.index[0],
                        "electrode_id": electrode.index[0],
                        "type": "EXT",
                        "unit": "V",
                        "sampling_frequency": ess[0].rate,
                        "gain": ess[0].conversion,
                    }
                    for electrode in electrodes
                ],
            }

    def convert_to_bids_session(
        self, bids_directory: str | pathlib.Path, copy_mode: typing.Literal["move", "copy", "symlink"] = "symlink"
    ) -> None:
        """
        Convert the NWB file to a BIDS session directory.

        Parameters
        ----------
        bids_directory : directory path
            The path to the directory where the BIDS dataset will be created.
        copy_mode : one of "move", "copy", or "symlink"
            Specifies how to handle the NWB files when converting to BIDS format.
            - "move": Move the files to the BIDS directory.
            - "copy": Copy the files to the BIDS directory.
            - "symlink": Create symbolic links to the files in the BIDS directory.
        """
        bids_directory = pathlib.Path(bids_directory)
        bids_directory.mkdir(exist_ok=True)

        if self.session_metadata is None:
            self.extract_session_metadata()

        session_subdirectory = bids_directory / "TODO"
        session_subdirectory.mkdir(exist_ok=True)

        if copy_mode == "copy":
            pass
        elif copy_mode == "move":
            pass
        elif copy_mode == "symlink":
            pass
