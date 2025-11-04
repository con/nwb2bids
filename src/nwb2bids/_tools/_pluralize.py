def _pluralize(n: int, word: str, plural: str | None = None) -> str:
    if n == 1:
        return word
    else:
        if plural is None:
            plural = word + "s"
        return plural
