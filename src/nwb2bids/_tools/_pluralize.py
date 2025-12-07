def _pluralize(n: int, phrase: str, plural: str | None = None) -> str:
    if n == 1:
        return phrase
    elif plural is None:
        return phrase + "s"
    else:
        return plural
