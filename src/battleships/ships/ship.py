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
from typing import Any, Mapping, Optional, Self, TYPE_CHECKING

# Third-party imports
from pydantic import (BaseModel,
                      ConfigDict,
                      field_validator,
                      model_validator,
                      PrivateAttr)
from pydantic_core.core_schema import ValidationInfo

# Local application imports
from .spec import ShipSpec
from .position import Position, PositionField

from utils import Divider

if TYPE_CHECKING:
    from board_games.coordinate import CoordLike

# Module-level constants

__all__ = ['Ship']


class Ship(BaseModel):
    """Concrete ship instance built from a ``ShipSpec`` and a placement.

    Combine a ``ShipSpec`` from a ``Roster`` with the player's position for
    a given ship to create a valid ``Ship`` instance.

    Attributes:
        spec: Ship's shared immutabl specification.
        type_index: Ordinal of this Ship within its type in a fleet. This lets
                    `Fleet` uniquely identify ships that share a common
                    `ShipSpec`.
        symbol: Ship's symbol to render.
        placement: Coordinates occupied by this ship.
    """
    model_config = ConfigDict(frozen=False, validate_default=True)

    spec: 'ShipSpec'
    type_index: int
    symbol: Optional[str] = None
    placement: Optional[PositionField] = None

    _hits: list[bool] = PrivateAttr(default_factory=list)

    def model_post_init(self, context: Any, /) -> None:
        if self.symbol is None:
            self.symbol = self.spec.symbol

        self._resize_hits()

    def _resize_hits(self) -> None:
        """Size `_hits` vector to `spec.size` IFF `placement` exists."""
        if self.placement is None:
            self._hits = []
        else:
            self._hits = [False] * self.spec.size

    @field_validator('placement', mode='before')
    @classmethod
    def _coerce_placement(cls, v: Any, info: ValidationInfo) -> Position | None:
        if v is None:
            return None

        if not isinstance(v, Mapping):
            return Position.coerce(v)

        idx = info.data.get('type_index')
        return (Position.coerce(v)
                if idx is None
                else Position.from_node(v, index=int(idx)))

    @field_validator('placement', mode='after')
    @classmethod
    def _check_ship_size_and_resize(
            cls, placement: 'Position', info: ValidationInfo
    ) -> Optional[Position]:
        """Confirm loaded ship is of the correct size.

        Also checks related fields. Might need to turn this method into
        `model_validator.
        """

        if placement is None:
            return None

        spec = info.data.get('spec')

        if isinstance(spec, ShipSpec) and placement.size != spec.size:
            raise ValueError(f"Expected ship size '{spec.size}' doesn't match "
                             f"placement size '{placement.size}'.")

        return placement

    @model_validator(mode='after')
    def _sync_runtime_state(self) -> Self:
        """Safe method to manage private attributes and finalise state."""
        if self.symbol is None:
            self.symbol = self.spec.symbol
        self._resize_hits()
        return self

    @property
    def type(self) -> str:
        """Ship type/classification."""
        return self.spec.type_name

    @property
    def remaining_tiles(self) -> int:
        """Tiles not yet hit on this ship."""
        if self.placement is not None:
            return self.spec.size - sum(self._hits)
        else:
            return 0

    @property
    def is_alive(self) -> bool:
        """Whether this ship is currently alive."""
        return self.remaining_tiles > 0

    @property
    def is_sunk(self) -> bool:
        """Whether this ship is currently sunk on the board."""
        return self.placement is not None and self.remaining_tiles == 0

    def load_placement(
            self, raw_node_or_coord_like: Any, index: Optional[int] = None
    ) -> Self:
        """Assign placement for this Ship.

        If a per-node type is provided, then use `self.index` unless `index` is
        provided.

        Arguments:
            raw_node_or_coord_like:
            index:
        """
        if isinstance(raw_node_or_coord_like, (Mapping, dict)):
            use_index = self.type_index if index is None else index
            self.placement = Position.from_node(raw_node_or_coord_like, index=use_index)
        else:
            self.placement = Position.coerce(raw_node_or_coord_like)  # triggers validator

        self._resize_hits()
        return self

    def take_hit(self, coord_like: CoordLike) -> tuple[bool, bool]:
        """Handle a shot against this ship and apply a hit if successful."""
        if self.placement is None or self.spec.size == 0 or self.is_sunk:
            return False, False

        # Defensive guard while debugging
        if len(self._hits) != self.spec.size:
            self._resize_hits()

        coord = Position.coerce(coord_like).positions[0]
        try:
            idx = self.placement.index(coord)
        except ValueError:
            return False, self.is_sunk

        if self._hits[idx]:
            return False, self.is_sunk

        self._hits[idx] = True
        return True, self.is_sunk

    def reset_hits(self) -> None:
        self._resize_hits()

    def __str__(self) -> str:
        return (f"<{self.__class__.__name__} "
                f"'{self.type!r}_{self.type_index!r}> "
                f"(alive={self.is_alive}, "
                f"remaining={self.remaining_tiles})")

    def __repr__(self):
        return (
            Divider.section.make_title('Ship', details=self.type, width=1)
            + str(self.placement) + str(self.spec))
