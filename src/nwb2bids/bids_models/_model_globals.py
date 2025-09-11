_VALID_PARTICIPANT_ID_REGEX = r"^[A-Za-z0-9]+$"
_VALID_SPECIES_REGEX = r"([A-Z][a-z]* [a-z]+)|(http://purl.obolibrary.org/obo/NCBITaxon_\d+)"
_VALID_BIDS_SEXES = {
    value: True
    for value in [
        "male",
        "m",
        "M",
        "MALE",
        "Male",
        "female",
        "f",
        "F",
        "FEMALE",
        "Female",
        "other",
        "o",
        "O",
        "OTHER",
        "Other",
    ]
}
_VALID_ARCHIVES_SEXES = {
    value: True
    for value in [
        "M",
        "F",
        "O",
        "U",
    ]
}
