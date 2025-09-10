_INVALID_PARTICIPANT_ID_REGEX = r".*[\s_]"
_VALID_SPECIES_REGEX = r"([A-Z][a-z]* [a-z]+)|(http://purl.obolibrary.org/obo/NCBITaxon_\d+)"
_ALLOWED_SEXES = {
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
