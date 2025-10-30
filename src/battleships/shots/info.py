#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file info.py)

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
from typing import Optional, TypeAlias, TYPE_CHECKING

# Third-party imports
from pydantic import ConfigDict, BaseModel

# Local application imports

if TYPE_CHECKING:
    from board_games.coordinate import Coordinate
    from battleships.shots import Outcome

# Module-level constants

__all__ = ['Shots', 'Info']


class Info(BaseModel):
    """Key information about each guess.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)
    coord: Coordinate
    outcome: Outcome
    ship_type: Optional[str] = None
    ship_index: Optional[int] = None
    repeat: bool = False


Shots: TypeAlias = list['Info']
"""A module-level constant with in-line docstring."""

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
