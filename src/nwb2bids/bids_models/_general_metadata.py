# import json
# import typing

# import pydantic
# import pynwb
#
#
# class EcephysMetadata(pydantic.BaseModel):
#     """
#     General device and session metadata extracted from NWB files.
#
#     While NWB treats this information as high-level session-specific metadata, BIDS treats these fields as
#     modality specific and as pertaining to 'parameters' that can vary.
#
#     This should typically be written to two files:
#       - `acq-general_ecephys.json`
#       - `acq-
#     """
#
#     InstitutionName: str = pydantic.Field(
#         description="The name of the institution in charge of the equipment that produced the measurements."
#     )
#
#     model_config = pydantic.ConfigDict(
#         validate_assignment=True,  # Re-validate model on mutation
#         extra="allow",  # Allow additional custom fields
#     )
#
#     @classmethod
#     @pydantic.validate_call
#     def from_nwbfiles(cls, nwbfiles: list[pynwb.NWBFile]) -> typing_extensions.Self:
#         """
#         Extracts all unique general metadata from the in-memory NWBFile objects.
#         """
#         institution_names = {nwbfile.institution for nwbfile in nwbfiles if nwbfile.institution is not None}
#
#         general_metadata = cls(
#             InstitutionName=institution_names,
#         )
#         return subject
#
#     @pydantic.validate_call
#     def to_json(self, file_path: str | pathlib.Path) -> None:
#         """
#         Save the general metadata to a JSON file.
#
#         Parameters
#         ----------
#         file_path : str or pathlib.Path
#             The path to the file where the metadata will be saved.
#         """
#         with file_path.open(mode="w") as file_stream:
#             json.dump(obj=self.model_dump(), fp=file_stream, indent=4)
