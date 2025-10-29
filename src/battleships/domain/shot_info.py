#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file shot_info.py)

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
        src/battleships/domain/shot_info.py
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
from enum import StrEnum
from typing import Any, Optional, Protocol, TypeAlias

# Third-party imports
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, field_validator, BaseModel

# Local application imports
from src.battleships.domain.coordinate import Coordinate


# Module-level constants
Shots: TypeAlias = list["ShotInfo"]
"""A module-level constant with in-line docstring."""

__all__ = ['Shots', 'ShotOutcome', 'ShotInfo', 'ShotEngine']


class ShotOutcome(StrEnum):
    """Possible outcomes of a shot at a valid Coordinate.

    Attributes:
        HIT: Successful shot.
        MISS: Unsuccessful shot.
        REPEAT: Take another shot.
        OUT: Out-of-bounds.
        INVALID: Coordinates were invalid.
        ERROR: Error encountered.
    """

    # Members: name becomes a human label (str), e.g. "Hit"
    HIT = "Hit! You struck an enemy ship."
    MISS = "Miss. Nothing struck."
    REPEAT = "You've already targeted that cell."
    OUT = "Shot is out of bounds."
    INVALID = "Coordinate input was invalid."
    ERROR = "Error encountered."

    def __new__(cls, message: str):
        obj = str.__new__(cls, message)
        obj._value_ = str(message)

        return obj

    def __str__(self) -> str:
        return self.name.capitalize().replace("_", " ")

    @property
    def message(self) -> str:
        """Verbose description of the outcome.

        Alias for the value of the Enum member.
        """
        return self._value_


class BoardProto(Protocol):
    def in_bounds(self, coord_like: Any) -> bool: ...
    def get(self, coord_like: Any) -> str: ...
    def mark_hit(self, coord_like: Any) -> None: ...
    def mark_miss(self, coord_like: Any) -> None: ...


class FleetProto(Protocol):
    def ship_at(self, coord_like: Any) -> tuple[Optional[Any], Optional[int]]: ...
    def register_shot(self, coord_like: Any) -> tuple['ShotOutcome', Optional[Any]]: ...


class ShotInfo(BaseModel):
    """Key information about each guess.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)
    coord: Coordinate
    outcome: ShotOutcome
    ship_type: Optional[str] = None
    ship_index: Optional[int] = None
    repeat: bool = False


class ShotEngine:
    """Pure, centralised shot rules."""

    @staticmethod
    def coerce(shot_like: Any) -> tuple[Optional[Coordinate], Optional[str]]:
        try:
            return Coordinate.coerce(shot_like), None
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"

    @staticmethod
    def process(target_board:BoardProto,
                target_fleet: FleetProto,
                shot_like: Any) -> ShotInfo:
        """Proceedings.

        Order of checks:
        1. coerce -> INVALID
        2. in_bounds -> OUT
        3. board cell repeat -> REPEAT
        4. fleet.register_shot -> HIT/MISS
        """
        coord, err = ShotEngine.coerce(shot_like)
        if coord is None:
            return ShotInfo(coord=Coordinate(0, 0),
                            outcome=ShotOutcome.INVALID)

        if not target_board.in_bounds(coord):
            return ShotInfo(coord=coord,
                            outcome=ShotOutcome.OUT)

        cell = target_board.get(coord)

        if cell in (ShotOutcome.HIT, ShotOutcome.MISS):
            return ShotInfo(coord=coord,
                            outcome=ShotOutcome.REPEAT,
                            repeat=True)

        outcome, ship = target_fleet.register_shot(coord)

        if outcome is ShotOutcome.MISS:
            target_board.mark_miss(coord)
            return ShotInfo(coord=coord,
                            outcome=ShotOutcome.MISS)

        if outcome is ShotOutcome.HIT:
            target_board.mark_hit(coord)
            ship_type = getattr(ship, 'type', None)
            ship_index = getattr(ship, 'index', None)
            return ShotInfo(coord=coord,
                            outcome=ShotOutcome.HIT,
                            ship_type=ship_type, ship_index=ship_index)

        return ShotInfo(coord=coord,
                        outcome=outcome or ShotOutcome.ERROR)

#
# class ShotInfo(BaseModel):
#     """Key information about each guess.
#
#     Attributes:
#         idx:               The index of the shot used to track.
#         coord:              Grid co-ordinate of the shot.
#         has_hit:            Whether the shot hit an enemy ship.
#     """
#     model_config = ConfigDict(validate_assignment=True)
#
#     coord: Coord
#     has_hit: Optional[bool] = None
#
#     @field_validator('coord', mode='before')
#     @classmethod
#     def _validate_coord(cls, v: Any) -> Coord:
#         """"""
#         is_shot_valid, coord, err_msg = Coord.convert(v)
#
#         if not is_shot_valid or coord is None:
#             raise ValueError(f"Invalid Coord string: {v!r}{err_msg}")
#         return coord
#
#     @classmethod
#     def from_shot(cls, shot: Any) -> "ShotInfo | None":
#         """Register this ShotInfo."""
#         is_valid, coord, err_msg = Coord.convert(shot)
#
#         if coord is None or not is_valid:
#             # Failure conditions.
#             return None
#
#         return ShotInfo(coord=coord)
#
