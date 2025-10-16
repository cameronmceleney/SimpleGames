#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file coordinates.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

(
Trailing paragraphs summarising final details.
)

Todo:

References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/battleships/domain/coordinates.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        14 Oct 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from typing import Any

# Third-party imports
from pydantic import (
    AliasChoices,
    BaseModel,
    ConfigDict,
    Field,
    field_validator)

# Local application imports

__all__ = ['Coord']


# Module-level constants
Coord = tuple[int, int]


class Placement(BaseModel):
    """"""
    positions: list[Coord] = Field(
        validation_alias=AliasChoices('positions', 'position')
    )

    @field_validator('positions', mode='before')
    @classmethod
    def _obtain_positions(cls, value: Any):
        """Obtains coordinate positions.

        Accept the following formats:
            -
        """
