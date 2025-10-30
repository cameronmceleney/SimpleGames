#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file position.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of placement.py). Note that leading symbol '>>>' includes the 
    code in doctests, while '$' does not.)::
        
        >>> bar = 1
        >>> foo = bar + 1

(
Trailing paragraphs summarising final details.
)

Todo:
    * (Optional section for module-wide tasks).
    * (Use format: 'YYMMDD/task_identifier - one-liner task description'
    
References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/battleships/domain/placement.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        24 Oct 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from collections.abc import Mapping
from typing import Annotated, Any, Iterator, Sequence, TypeAlias

# Third-party imports
from pydantic import (AliasChoices,
                      BaseModel,
                      BeforeValidator,
                      computed_field,
                      ConfigDict,
                      Field,
                      field_validator)

# Local application imports
from board_games.coordinate import Coordinate
from src.utils.utils import JustifyText

__all__ = [
    'position_type',
    'POSITION_ALIASES',
    'Position',
    'PositionField'
]


# Module-level constants
position_type: TypeAlias = tuple[Coordinate, ...]
"""Data-type of ``Position.positions``."""

POSITION_ALIASES: tuple[str, ...] = ('positions', 'position')
"""Valid aliases for loading a position."""


class Position(BaseModel):
    """A ship's placement on a 2D grid.

    Represents an ordered, immutable sequence of ``Coordinate`` objects.

    Attributes:
        positions:

    TODO:
        - Add a `load_from_yaml` helper
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    positions: position_type = Field(
        ...,
        validation_alias=AliasChoices(*POSITION_ALIASES),
        description="Ordered coordinates for this ship."
    )

    @field_validator('positions', mode='before')
    @classmethod
    def _coerce_positions(cls, v: Any) -> position_type:
        """"""
        if v is None:
            raise ValueError("Positions cannot be None")

        if isinstance(v, Mapping):
            return cls._from_mapping(v)

        if isinstance(v, (list, tuple)):
            return cls._from_sequence(v)
        elif (isinstance(v, Sequence)
                and not isinstance(v, (str, bytes, bytearray))):
            return cls._from_sequence(v)

        # Last chance
        return cls._from_single(v)

    @field_validator('positions', mode='after')
    @classmethod
    def _ensure_unique(cls, positions: position_type) -> position_type:
        """Prevents duplicate ``Coordinate`` objects from being stored.

        Arguments:
            positions:
        """
        if len(positions) == len(set(positions)):
            return positions

        # Find duplicate coordinates to generate useful error message
        seen: set[Coordinate] = set()
        duplicates: list[Coordinate] = []

        for coord in positions:
            if coord in seen:
                duplicates.append(coord)
            else:
                seen.add(coord)

        duplicates.sort(key=lambda c: (c.x, c.y))
        raise ValueError(f"Duplicate coordinates not allowed: {duplicates!r}")

    @classmethod
    def _extract_coords_from_mapping(cls, m: Mapping[str, Any]):
        keys = [k for k in POSITION_ALIASES if k in m]
        if not keys:
            raise ValueError('No position (or valid alias) key found.')

        if len(keys) > 1:
            raise ValueError(f"Too many position keys.")

        return m[keys[0]]  # indexing required

    @classmethod
    def _from_mapping(cls, m: Mapping[str, Any]) -> position_type:
        """Generate from a mapping of position-like objects."""
        return cls._coerce_positions(
            cls._extract_coords_from_mapping(m)
        )

    @classmethod
    def _from_sequence(cls, seq: Sequence[Any]) -> position_type:
        """Generate from a sequence of position-like objects."""
        return tuple(Coordinate.coerce(item) for item in seq)

    @classmethod
    def _from_single(cls, item: Any) -> position_type:
        """Attempt to generate from a single position-like object."""
        try:
            return (Coordinate.coerce(item),)
        except Exception as e:
            raise ValueError(f"Invalid position: {item!r} ({e})") from e

    @classmethod
    def from_raw(cls, *coords_like: Any) -> Position:
        """Convenience builder.

        Pydantic models accept one argument per field, so this method offers an
        approach most similar to ``Position([1,2],[2,3])``.

        Arguments:
            coords_like: ``Coordinate`` objects or object(s) of a type that be
                         used to create ``Coordinate`` objects.
        """
        return cls(positions=coords_like)

    @classmethod
    def from_node(cls, node: Mapping[str, Any], *, index: int) -> 'Position':
        """Extract a position from a per-type node.

        Required when generating ``Position`` objects from configuration files.

        Arguments:
            node: Input data
            index: Ordinal index to identify which data should be extracted if
                   the mapping is one-to-many.
        """
        if not isinstance(node, Mapping):
            raise TypeError(f"Expected mapping node, "
                            f"but got {type(node).__name__}.")

        payload = cls._extract_coords_from_mapping(node)

        if isinstance(payload, list):
            try:
                part = payload[index]
            except IndexError:
                raise IndexError(f"No placement at index {index!r} "
                                 f"(len={len(payload)}).")
            return cls(positions=part)

        if index != 0:
            raise ValueError(f"Single placement provided "
                             f"but index={index} requested.")

        return cls(positions=payload)

    @classmethod
    def coerce(cls, v: Any) -> 'Position':
        """Adapter to convert an input into a valid ``Position`.

        For use in cases where one would try to directly call the class.
        """
        return v if isinstance(v, cls) else cls(positions=v)

    @computed_field
    def size(self) -> int:
        """Returns the size of the position.

        Method is included to allow consistent use of `self.obj.size` within
        `Ship` when referring to either `Position` or `ShipSpec`.
        """
        return len(self.positions)

    @computed_field
    def __len__(self) -> int:
        return len(self.positions)

    def __iter__(self) -> Iterator[Coordinate]:
        return iter(self.positions)

    def __getitem__(self, index: int) -> Coordinate:
        return self.positions[index]

    def __str__(self):
        return JustifyText.kv('Positions', self.positions)


PositionField: TypeAlias = Annotated[
    Position,
    BeforeValidator(Position.coerce)]
"""Use this alias of `Position` when initialising a `Field` in Pydantic."""
