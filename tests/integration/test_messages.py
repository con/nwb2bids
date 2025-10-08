"""Tests for message handling passed to the top-level `converter_nwb_dataset` function."""

import pathlib

import nwb2bids


def test_messages_baseline(minimal_nwbfile_path: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [minimal_nwbfile_path]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    assert len(messages) == 0


def test_messages_1(problematic_nwbfile_path_1: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_1]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionResult(
            title="Invalid species",
            reason="Participant species is not a proper Latin binomial or NCBI Taxonomy id.",
            solution=(
                "Rename the subject species to a Latin binomial, obolibrary taxonomy link, or NCBI taxonomy "
                "reference."
            ),
            examples=[],
            field="nwbfile.subject.species",
            source_file_paths=nwb_paths,
            data_standards=[nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.SCHEMA_INVALIDATION,
            severity=nwb2bids.Severity.ERROR,
        ),
        nwb2bids.InspectionResult(
            title="Invalid participant ID",
            reason=(
                "The participant ID contains invalid characters. BIDS allows only dashes to be used as separators in "
                "subject entity label. Underscores, spaces, slashes, and special characters (including #) are "
                "expressly forbidden."
            ),
            solution="Rename the subject without using spaces or underscores.",
            examples=["`ab_01` -> `ab-01`", "`subject #2` -> `subject-2`", "`id 2 from 9/1/25` -> `id-2-9-1-25`"],
            field="nwbfile.subject.subject_id",
            source_file_paths=nwb_paths,
            data_standards=[nwb2bids.DataStandard.BIDS, nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.ERROR,
        ),
        nwb2bids.InspectionResult(
            title="Invalid participant sex (BIDS)",
            reason="Participant sex is not one of the allowed patterns by BIDS.",
            solution="Rename the subject sex to be one of the accepted values.",
            examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            field="nwbfile.subject.sex",
            source_file_paths=nwb_paths,
            data_standards=[nwb2bids.DataStandard.BIDS],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.ERROR,
        ),
        nwb2bids.InspectionResult(
            title="Invalid participant sex (archives)",
            reason="Participant sex is not one of the allowed patterns by the common archives.",
            solution="Rename the subject sex to be one of the accepted values.",
            examples=["`male` -> `M`", "`Female` -> `F`", "`n/a` -> `U`", "`hermaphrodite` -> `O`"],
            field="nwbfile.subject.sex",
            source_file_paths=nwb_paths,
            data_standards=[nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.ERROR,
        ),
    ]
    assert messages == expected_messages


def test_messages_2(problematic_nwbfile_path_2: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_2]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionResult(
            title="Missing participant sex",
            reason="Archives such as DANDI or EMBER require the subject sex to be specified.",
            solution=(
                "Specify the `sex` field of the Subject object attached to the NWB file as one of four options: "
                '"M" (for male), "F" (for female), "U" (for unknown), or "O" (for other).\nNOTE: for certain animal '
                'species with more specific genetic determinants, such as C elegans, use "O" (for other) then further '
                'specify the subtypes using other custom fields. For example, `c_elegans_sex="XO"`'
            ),
            examples=None,
            field="nwbfile.subject.sex",
            source_file_paths=nwb_paths,
            target_file_paths=None,
            data_standards=[nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.SCHEMA_INVALIDATION,
            severity=nwb2bids.Severity.CRITICAL,
        ),
        nwb2bids.InspectionResult(
            title="Missing participant species",
            reason="Archives such as DANDI or EMBER require the subject species to be specified.",
            solution=(
                "Specify the `species` field of the Subject object attached to the NWB file as a Latin binomial, "
                "obolibrary taxonomy link, or NCBI taxonomy reference."
            ),
            examples=None,
            field="nwbfile.subject.species",
            source_file_paths=nwb_paths,
            target_file_paths=None,
            data_standards=[nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.SCHEMA_INVALIDATION,
            severity=nwb2bids.Severity.CRITICAL,
        ),
        nwb2bids.InspectionResult(
            title="Invalid participant ID",
            reason=(
                "The participant ID contains invalid characters. BIDS allows only dashes to be used as separators in "
                "subject entity label. Underscores, spaces, slashes, and special characters (including #) are "
                "expressly forbidden."
            ),
            solution="Rename the subject without using spaces or underscores.",
            examples=["`ab_01` -> `ab-01`", "`subject #2` -> `subject-2`", "`id 2 from 9/1/25` -> `id-2-9-1-25`"],
            field="nwbfile.subject.subject_id",
            source_file_paths=nwb_paths,
            target_file_paths=None,
            data_standards=[nwb2bids.DataStandard.BIDS, nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.ERROR,
        ),
        nwb2bids.InspectionResult(
            title="Invalid session ID",
            reason=(
                "The session ID contains invalid characters. "
                "BIDS allows only dashes to be used as separators in session entity label. "
                "Underscores, spaces, slashes, and special characters (including #) are expressly forbidden."
            ),
            solution="Rename the session without using spaces or underscores.",
            examples=[
                "`ses_01` -> `ses-01`",
                "`session #2` -> `session-2`",
                "`id 2 from 9/1/25` -> `id-2-9-1-25`",
            ],
            field="nwbfile.session_id",
            source_file_paths=nwb_paths,
            data_standards=[nwb2bids.DataStandard.BIDS, nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.ERROR,
        ),
    ]
    assert messages == expected_messages


def test_messages_3(problematic_nwbfile_path_3: pathlib.Path, temporary_bids_directory: pathlib.Path) -> None:
    nwb_paths = [problematic_nwbfile_path_3]
    messages = nwb2bids.convert_nwb_dataset(nwb_paths=nwb_paths, bids_directory=temporary_bids_directory)

    expected_messages = [
        nwb2bids.InspectionResult(
            title="Missing participant",
            reason="BIDS requires a subject to be specified for each NWB file.",
            solution="Add a Subject object to each NWB file.",
            examples=None,
            field="nwbfile.subject",
            source_file_paths=nwb_paths,
            target_file_paths=None,
            data_standards=[nwb2bids.DataStandard.BIDS, nwb2bids.DataStandard.DANDI],
            category=nwb2bids.Category.STYLE_SUGGESTION,
            severity=nwb2bids.Severity.CRITICAL,
        )
    ]
    assert messages == expected_messages
