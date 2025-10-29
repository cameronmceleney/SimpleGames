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

import yaml
# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      Field,
                      field_validator,
                      model_validator,
                      PrivateAttr)
from pydantic_core.core_schema import ValidationInfo

# Local application imports
from src.battleships.domain.position import Position, PositionField
from src.utils.utils import CleanText, JustifyText, Divider

# Module-level constants

__all__ = ['ShipSpec', 'Ship']


class ShipSpec(BaseModel):
    """Base property used to define all ships.

    Attributes:
        size: Number of tiles/squares spanned by the ship.
        is_cloaked: If ``True``, **ship is not displayed with markers**,
                    after being hit, for the opposing player/players.
        default_symbol: Single character used to represent the ship.
        type: Category of ship (e.g. cruiser) which also dictates what concrete
              instances of this ShipSpec instance are called during the game.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    size: int = Field(..., gt=0)
    is_cloaked: bool = False
    symbol: Optional[str] = Field(None, min_length=1, max_length=1)

    type_name: str = Field(..., min_length=1)

    @field_validator('symbol', mode='before')
    @classmethod
    def _validate_symbol(cls, v: Optional[str], info: ValidationInfo) -> str | None:
        if v is None:
            t = info.data.get('type_name')
            if isinstance(t, str) and t:
                return t[0].upper()
            return None

        # Coerce to string and enforce 1 char
        v = str(v)

        if len(v) != 1:
            raise ValueError(f"Symbol must be a single character "
                             f"but got {v!r}")

        return v

    def __str__(self) -> str:
        return f"<{self.__class__.__name__} '{self.type_name}'> (size={self.size})"

    def __repr__(self):
        return (
            JustifyText.kv('Type', f"{self.type_name}")
            + JustifyText.kv('Size', f"{self.size} tiles")
            + JustifyText.kv('Cloaked?', CleanText.truthy(self.is_cloaked))
            + JustifyText.kv('Symbol', self.symbol or '-')
        )


class Ship(BaseModel):
    """Ship definition used to create ships in a fleet.

    Combine a ``ShipSpec`` from a ``Roster`` with the player's position for
    a given ship to create a valid ``Ship`` instance.

    Attributes:
        spec: Ship's specification.
        index: Ordinal of this Ship within its type. This lets `Fleet`
               uniquely identify ships that share a common `ShipSpec`.
        placement: Positions on the board occupied by this ship.

        _is_alive:          Tracks whether the ship has been destroyed.

        _is_placed:         Has this ship been placed (i.e. *loaded*) onto the game's board.

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

        if self.symbol is None and self.spec.symbol is not None:
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

    def _coerce_coord_inline(self, v: Any) -> Coordinate:
        from src.battleships.domain.coordinate import Coordinate
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
