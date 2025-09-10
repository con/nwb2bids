import pydantic


class InspectionMessage(pydantic.BaseModel):
    title: str = pydantic.Field(description="Short title of the issue.")
    text: str = pydantic.Field(description="Detailed description of the issue and suggestions for how to resolve it.")
    level: int = pydantic.Field(
        description=(
            "Quantifier of relative severity (how important it is to resolve). "
            "The larger the value, the more critical it is."
        ),
        ge=0,
    )

    model_config = pydantic.ConfigDict(frozen=True)
