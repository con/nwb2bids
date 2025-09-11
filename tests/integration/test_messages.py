"""Tests for message handling passed to the top-level `converter_nwb_dataset` function."""

import pathlib

import nwb2bids


def test_messages_1(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_1]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionMessage(
            title="Invalid participant ID",
            reason=(
                "The participant ID contains invalid characters. BIDS allows only dashes to be used as separators in "
                "subject entity label. Underscores, spaces, slashes, and special characters (including #) are "
                "expressly forbidden."
            ),
            solution="Rename the participants without using spaces or underscores.",
            examples=["`ab_01` -> `ab-01`", "`subject #2` -> `subject-2`", "`id 2 from 9/1/25` -> `id-2-9-1-25`"],
            location_in_file="nwbfile.subject.subject_id",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.INVALID_BIDS_VALUE,
        ),
        nwb2bids.InspectionMessage(
            title="Invalid subject sex (BIDS)",
            reason="Subject sex is not one of the allowed patterns by BIDS.",
            solution="Rename the subject sex to be one of the accepted values.",
            examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            location_in_file="nwbfile.subject.sex",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.INVALID_BIDS_VALUE,
        ),
        nwb2bids.InspectionMessage(
            title="Invalid species",
            reason="Subject species is not a proper Latin binomial or NCBI Taxonomy id.",
            solution=(
                "Rename the participants species to a Latin binomial, obolibrary taxonomy link, or NCBI taxonomy "
                "reference."
            ),
            examples=[],
            location_in_file="nwbfile.subject.species",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.INVALID_ARCHIVE_VALUE,
        ),
        nwb2bids.InspectionMessage(
            title="Invalid subject sex (archives)",
            reason="Subject sex is not one of the allowed patterns by the common archives.",
            solution="Rename the subject sex to be one of the accepted values.",
            examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            location_in_file="nwbfile.subject.sex",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.INVALID_ARCHIVE_VALUE,
        ),
    ]
    assert messages == expected_messages


def test_messages_2(problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_2]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionMessage(
            title="Invalid participant ID",
            reason=(
                "The participant ID contains invalid characters. BIDS allows only dashes to be used as separators in "
                "subject entity label. Underscores, spaces, slashes, and special characters (including #) are "
                "expressly forbidden."
            ),
            solution="Rename the participants without using spaces or underscores.",
            examples=["`ab_01` -> `ab-01`", "`subject #2` -> `subject-2`", "`id 2 from 9/1/25` -> `id-2-9-1-25`"],
            location_in_file="nwbfile.subject.subject_id",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.INVALID_BIDS_VALUE,
        ),
        nwb2bids.InspectionMessage(
            title="Missing participant sex",
            reason="Archives such as DANDI or EMBER require the subject sex to be specified.",
            solution=(
                "Specify the `sex` field of the Subject object attached to the NWB file as one of four options: "
                '"M" (for male), "F" (for female), "U" (for unknown), or "O" (for other).\nNOTE: for certain animal '
                'species with more specific genetic determinants, such as C elegans, use "O" (for other) then further '
                'specify the subtypes using other custom fields. For example, `c_elegans_sex="XO"`'
            ),
            examples=None,
            location_in_file="nwbfile.subject.sex",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.MISSING_ARCHIVE_FIELD,
        ),
        nwb2bids.InspectionMessage(
            title="Missing participant species",
            reason="Archives such as DANDI or EMBER require the subject species to be specified.",
            solution=(
                "Specify the `species` field of the Subject object attached to the NWB file as a Latin binomial, "
                "obolibrary taxonomy link, or NCBI taxonomy reference."
            ),
            examples=None,
            location_in_file="nwbfile.subject.species",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.MISSING_ARCHIVE_FIELD,
        ),
    ]
    assert messages == expected_messages


def test_messages_3(problematic_nwbfile_path_3: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_3]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionMessage(
            title="Missing subject",
            reason="BIDS requires a subject to be specified for each NWB file.",
            solution="Add a Subject object to each NWB file.",
            examples=None,
            location_in_file="nwbfile.subject",
            file_paths=nwb_paths,
            level=nwb2bids.InspectionLevel.MISSING_BIDS_ENTITY,
        )
    ]
    assert messages == expected_messages
