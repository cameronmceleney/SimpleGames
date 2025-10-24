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

Todo:

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
from typing import Any

# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      Field, field_validator,
                      model_validator,
                      PrivateAttr, AliasChoices)

from pydantic.dataclasses import dataclass

from battleships.domain.position import coerce_position
# Local application imports
from src.battleships.domain.coordinate import Coordinate
from src.battleships.domain.position import Position, POSITION_ALIASES, PositionField
from src.utils.utils import clean_string, truthy_to_printable, JUST_L_WIDTH

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
        return (f"{"Size":<{JUST_L_WIDTH}}{self.size} tiles\n"
                f"{"Cloaked?":<{JUST_L_WIDTH}}{truthy_to_printable(self.is_cloaked)}")


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
    placement: PositionField = Field(
        ...,
        validation_alias=AliasChoices(*POSITION_ALIASES))

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

    def update_position(self, pos) -> None:
        """"""
        if isinstance(pos, Coordinate):
            self.pos = pos
        else:
            self.pos = Coordinate(pos)
        self._is_placed = True

    def __str__(self):
        return (f"<Ship> {self.type}\n"
                f"{'-' * 8}\n"
                f"{self.pos}\n"
                f"{self.spec}")


if __name__ == "__main__":
    ship = Ship(spec=ShipSpec(size=5),
                type='cruiser',
                placement=[[1, 2], [2, 3]])
    print(ship)
