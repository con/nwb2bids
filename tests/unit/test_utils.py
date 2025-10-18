import pathlib

import nwb2bids


def test_create_file_tree(testing_files_directory: pathlib.Path) -> None:
    test_directory = testing_files_directory / "test_file_tree_from_dict"
    test_directory.mkdir(exist_ok=True)

    test_structure = {
        "a": {
            "b": {
                "file1.txt": "Content of file 1",
                "file2.txt": "Content of file 2",
            },
            "c": {
                "d": {
                    "file3.txt": "Content of file 3",
                },
            },
        },
        "file4.txt": "Content of file 4",
    }
    nwb2bids.testing.create_file_tree(directory=test_directory, structure=test_structure)

    expected_structure = {
        test_directory: {
            "directories": {"a"},
            "files": {"file4.txt"},
        },
        test_directory
        / "a": {
            "directories": {"b", "c"},
            "files": set(),
        },
        test_directory
        / "a"
        / "b": {
            "directories": set(),
            "files": {"file1.txt", "file2.txt"},
        },
        test_directory
        / "a"
        / "c": {
            "directories": {"d"},
            "files": set(),
        },
        test_directory
        / "a"
        / "c"
        / "d": {
            "directories": set(),
            "files": {"file3.txt"},
        },
    }
    nwb2bids.testing.assert_subdirectory_structure(directory=test_directory, expected_structure=expected_structure)
