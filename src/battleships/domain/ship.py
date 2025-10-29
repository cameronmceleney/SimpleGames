#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file ship.py)

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

    >>> ship = Ship(spec=ShipSpec(size=2), type='cruiser', placement=Position.from_raw([1, 1], [1, 2]))

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

import doctest
from functools import cached_property
# Standard library imports
from typing import Any, Optional

# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      Field,
                      model_validator,
                      PrivateAttr)

# Local application imports
from src.battleships.domain.position import Position, PositionField
from src.utils.utils import CleanText, JustifyText, Divider

# Module-level constants

__all__ = ['ShipSpec', 'Ship']


class ShipSpec(BaseModel):
    """Base property used to define all ships.

    Attributes:
        size:           Number of tiles/squares spanned by the ship.

        is_cloaked:     If ``True``, **ship is not displayed with markers**,
                        after being hit, for the opposing player/players.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    size: int = Field(..., gt=0)
    is_cloaked: bool = False

    def __str__(self):
        return (JustifyText.kv('Size', f"{self.size} tiles")
                + JustifyText.kv('Cloaked?', CleanText.truthy(self.is_cloaked)))


class Ship(BaseModel):
    """Ship definition used to create ships in a fleet.

    Combine a ``ShipSpec`` from a ``Roster`` with the player's position for
    a given ship to create a valid ``Ship`` instance.

    Attributes:
        spec:               Ship's specification.

        type:                 Tag.

        position:                Position of the ship on the playing board.

        _is_alive:          Tracks whether the ship has been destroyed.

        _is_placed:         Has this ship been placed (i.e. *loaded*) onto the game's board.

    """
    model_config = ConfigDict(frozen=False, validate_default=True)

    spec: 'ShipSpec'
    type: str
    symbol: Optional[str] = None
    placement: Optional[PositionField] = None

    _is_alive: bool = PrivateAttr(default=True)
    _is_placed: bool = PrivateAttr(default=False)

    @model_validator(mode='after')
    def _check_size(self) -> 'Ship':
        if self.placement.size != self.spec.size:
            raise ValueError(
                f"Ship '{self.type}' expects {self.spec.size} tiles,"
                f"but got {self.placement.size}."
            )
        return self

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    def mark_destroyed(self) -> None:
        self._is_alive = False

    @property
    def is_placed(self) -> bool:
        return self._is_placed

    def mark_placed(self):
        self._is_placed = True

    def __str__(self):
        return (
            Divider.section.make_title('Ship', details=self.type, width=1)
            + str(self.placement) + str(self.spec))

# if __name__ == '__main__':
#     ship = Ship(spec=ShipSpec(size=2), type='cruiser', placement=Position.from_raw([1, 1], [1, 2]))
#     print(ship)
