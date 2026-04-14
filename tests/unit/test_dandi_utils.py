"""Unit tests for the `_dandi_utils` module."""

import pytest

from nwb2bids._converters._dandi_utils import _get_dataset_description_from_invalid_dandiset_metadata


@pytest.mark.ai_generated
@pytest.mark.parametrize(
    "contributors, expected_authors",
    [
        pytest.param(
            [
                {"name": "Author, One", "schemaKey": "Person", "roleName": ["dcite:Author"]},
                {"name": "Contact, Two", "schemaKey": "Person", "roleName": ["dcite:ContactPerson"]},
                {"name": "Some Org", "schemaKey": "Organization", "roleName": []},
            ],
            ["Author, One"],
            id="dcite_author_takes_precedence",
        ),
        pytest.param(
            [
                {"name": "Gouwens, Nathan", "schemaKey": "Person", "roleName": ["dcite:ContactPerson"]},
                {"name": "Allen Institute for Brain Science", "schemaKey": "Organization", "roleName": []},
            ],
            ["Gouwens, Nathan"],
            id="fallback_to_persons_excludes_orgs",
        ),
        pytest.param(
            [
                {"name": "Some Organization", "schemaKey": "Organization", "roleName": []},
            ],
            None,
            id="org_only_yields_none",
        ),
    ],
)
def test_author_extraction_from_invalid_metadata(contributors, expected_authors):
    """Author extraction: dcite:Author preferred, then Person fallback (skip Organizations)."""
    raw_metadata = {
        "name": "Test Dandiset",
        "assetsSummary": {"dataStandard": []},
        "contributor": contributors,
    }
    description, _ = _get_dataset_description_from_invalid_dandiset_metadata(raw_metadata=raw_metadata)
    assert description.Authors == expected_authors
