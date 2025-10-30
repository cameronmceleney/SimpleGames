#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file spec.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)

(
Trailing paragraphs summarising final details.
)


Examples:
    Create a ``Ship`` instance.

    >>> spec = ShipSpec(size=2, symbol='S', is_cloaked=False)

References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/battleships/domain/ship.py
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
import re
from typing import Optional

# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      Field,
                      field_validator,
                      ValidationInfo, model_validator)

# Local application imports
from utils import CleanText, JustifyText

# Module-level constants

__all__ = ['ShipSpec']


class ShipSpec(BaseModel):
    """Base property used to define all ships.

    Attributes:
        size: Number of tiles/squares spanned by the ship.
        is_cloaked: If ``True``, **ship is not displayed with markers**,
                    after being hit, for the opposing player/players.
        symbol: Single character used to represent the ship.
        type_name: Category of ship (e.g. cruiser) which also dictates what concrete
              instances of this ShipSpec instance are called during the game.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    size: int = Field(..., gt=0)
    is_cloaked: bool = False
    symbol: str | None = Field(None)
    type_name: str = Field(..., min_length=1)

    @model_validator(mode='after')
    def _validate_symbol(self) -> 'ShipSpec':

        candidate = self.symbol or self.type_name[0].upper()
        if len(candidate) != 1 or not re.compile(r'^[A-Za-z]'):
            raise ValueError(f"Symbol must be a single ASCII letter [A-Za-z],"
                             f"but got {candidate!r}.")

        if self.symbol != candidate:
            object.__setattr__(self, 'symbol', candidate)

        return self

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} '{self.type_name}'> (size={self.size})"

    def __repr__(self):
        return (
                JustifyText.kv('Type', f"{self.type_name}")
                + JustifyText.kv('Size', f"{self.size} tiles")
                + JustifyText.kv('Cloaked?', CleanText.truthy(self.is_cloaked))
                + JustifyText.kv('Symbol', self.symbol or '-')
        )
