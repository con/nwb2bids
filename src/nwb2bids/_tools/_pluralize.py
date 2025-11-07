def _pluralize(n: int, word: str, plural: str | None = None) -> str:
    if n == 1:
        return word
    elif plural is None:
        return word + "s"
    else:
        return plural
