import random
from typing import List, Optional

from pydantic import BaseModel, Field

from .base import Tool


# Inline description: the library must not depend on files outside the package.
DESCRIPTION = """# Random choice

Select exactly one item at random from the provided list of choices.

Use this tool when a decision must be random rather than based on preference,
ranking, or semantic reasoning. The `choices` parameter must contain at least one
string. The tool returns the selected string unchanged.
"""


class RandomChoicesArguments(BaseModel):
    choices: List[str] = Field(
        min_length=1,
        description="Non-empty list of strings from which one item will be selected.",
    )


class RandomChoicesTool(Tool):
    """Select one string at random from a list supplied by the model."""

    def __init__(
        self,
        verbose: bool = False,
        rng: Optional[random.Random] = None,
    ):
        self._rng = rng if rng is not None else random.Random()
        super().__init__(
            name="random_choices",
            description=DESCRIPTION,
            arguments=RandomChoicesArguments,
            handler=self._choose,
            verbose=verbose,
        )

    def _choose(self, choices: List[str]) -> str:
        return self._rng.choice(choices)
