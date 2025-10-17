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
from pydantic import BaseModel, ConfigDict, Field, field_validator, \
    model_validator, PrivateAttr
from pydantic.dataclasses import dataclass

# Third-party imports

# Local application imports
from src.battleships.domain.coordinates import Coord, Placement
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
        id:             Tag.

        pos:            Position of the ship on the playing board.

        is_alive:         Tracks whether the ship has been destroyed.

    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    spec: 'ShipSpec'
    id: str = ""
    pos: 'Placement' = Placement()

    _is_alive: bool = PrivateAttr(default=True)

    @property
    def is_alive(self) -> bool:
        return self._is_alive

    @property
    def mark_hit(self) -> None:
        raise NotImplementedError("This property is not implemented.")

    def mark_destroyed(self) -> None:
        self._is_alive = False

    def __str__(self):
        return (f"<Ship> {self.id}\n"
                f"{'-' * 8}\n"
                f"{self.pos}\n"
                f"{ship.spec}")


if __name__ == "__main__":
    ss = ShipSpec(size=5)
    ship = Ship(spec=ss)
    print(ship)
