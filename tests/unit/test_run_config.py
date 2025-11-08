import pathlib

import pydantic
import pytest

import nwb2bids


def test_run_config_immutability(temporary_bids_directory: pathlib.Path):
    run_config = nwb2bids.RunConfig(bids_directory=temporary_bids_directory)

    with pytest.raises(expected_exception=pydantic.ValidationError, match="Instance is frozen"):
        run_config.run_id = "new_run_id"
