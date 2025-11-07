"""Configuration file for the doctests."""

import pathlib
import typing

import pytest


# Doctest directories
@pytest.fixture(autouse=True)
def add_data_space(doctest_namespace: dict[str, typing.Any], tmp_path: pathlib.Path):
    doctest_namespace["path_to_some_directory"] = pathlib.Path(tmp_path)
