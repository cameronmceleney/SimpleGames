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

# Standard library imports
from typing import Any, Mapping, Optional

# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      field_validator,
                      model_validator,
                      PrivateAttr)
from pydantic_core.core_schema import ValidationInfo

# Local application imports
from board_games.coordinate import Coordinate
from .spec import ShipSpec
from .position import Position, PositionField

from utils import Divider

# Module-level constants

__all__ = ['Ship']


class Ship(BaseModel):
    """Ship definition used to create ships in a fleet.

    Combine a ``ShipSpec`` from a ``Roster`` with the player's position for
    a given ship to create a valid ``Ship`` instance.

    Attributes:
        spec: Ship's specification.
        index: Ordinal of this Ship within its type. This lets `Fleet`
               uniquely identify ships that share a common `ShipSpec`.
        placement: Positions on the board occupied by this ship.
    """
    model_config = ConfigDict(frozen=False, validate_default=True)

    spec: 'ShipSpec'
    index: int
    symbol: Optional[str] = None
    placement: Optional[PositionField] = None

    _hits: list[bool] = PrivateAttr(default_factory=list)

    @field_validator('placement', mode='before')
    @classmethod
    def _coerce_placement(cls, v: Any, info: ValidationInfo) -> Position | None:
        if v is None:
            return None

        # Select this ship's slice from the full node mapping
        if isinstance(v, Mapping):
            idx = info.data.get('index')
            if idx is None:
                return Position.coerce(v)  # Temporary fallback
            return Position.from_node(v, index=int(idx))

        return Position.coerce(v)

    @model_validator(mode='after')
    def _sync_placement_and_hits(self) -> 'Ship':
        if self.placement is None:
            self._hits.clear()
            return self

        # Confirm ship size is correct
        if self.placement.size != self.spec.size:
            raise ValueError(
                f"Ship '{self.type}' expects {self.spec.size} tiles,"
                f"but got {self.placement.size}."
            )

        if self.symbol is None:
            self.symbol = self.spec.symbol

        if len(self._hits) != self.spec.size:
            self._hits = [False] * self.spec.size

        return self

    def load_placement(
            self, raw_node_or_coord_like: Any, index: Optional[int] = None
    ) -> 'Ship':
        """Assign placement for this Ship.

        If a per-node type is provided, then use `self.index` unless `index` is
        provided.

        Arguments:
            raw_node_or_coord_like:
            index:
        """
        if isinstance(raw_node_or_coord_like, Mapping):
            use_index = self.index if index is None else index
            self.placement = Position.from_node(raw_node_or_coord_like, index=use_index)
        else:
            self.placement = raw_node_or_coord_like  # triggers validator

        return self

    @property
    def type(self) -> str:
        return self.spec.type_name

    @property
    def remaining_tiles(self) -> int:
        """Tiles not yet hit on this ship."""
        if self.placement is None:
            return 0

        return self.spec.size - sum(self._hits)

    @property
    def is_alive(self) -> bool:
        """Whether this ship is currently alive."""
        return self.remaining_tiles > 0

    @property
    def is_sunk(self) -> bool:
        """Whether this ship is currently sunk on the board."""
        return self.placement is not None and self.remaining_tiles == 0

    def register_shot(self, coord_like: Any) -> tuple[bool, bool]:
        """Record a shot against this ship.

        Always returns (False, False) if no placement is set.

        Returns: hit?, sunk?
        """
        if self.placement is None or self.spec.size == 0 or self.is_sunk:
            return False, False

        c = Position.coerce(coord_like).positions[0]
        try:
            idx = self.placement.positions.index(c)
        except ValueError:
            return False, self.is_sunk

        if self._hits and self._hits[idx]:
            return False, self.is_sunk

        self._hits[idx] = True
        return True, self.is_sunk

    @staticmethod
    def _coerce_coord_inline(v: Any) -> Coordinate:
        """Helper if Coordinate import leads to circular import.

        TODO:
            - Find a way to not need this method in `Ship`!
        """
        from board_games.coordinate import Coordinate
        return Coordinate.coerce(v)

    def reset_hits(self) -> None:
        self._hits = [False] * (self.spec.size if self.placement else 0)

    def __str__(self) -> str:
        return (f"<{self.__class__.__name__} '{self.type!r}_{self.index!r}> "
                f"(alive={self.is_alive}, remaining={self.remaining_tiles})")

    def __repr__(self):
        return (
            Divider.section.make_title('Ship', details=self.type, width=1)
            + str(self.placement) + str(self.spec))

# if __name__ == '__main__':
#     ship = Ship(spec=ShipSpec(size=2), type='cruiser', placement=Position.from_raw([1, 1], [1, 2]))
#     print(ship)
