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
from typing import Any, Optional, TypeAlias

# Third-party imports
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict, field_validator

# Local application imports
from src.battleships.domain.coordinates import Coord

# Module-level constants
Shots: TypeAlias = list["ShotInfo"]
"""A module-level constant with in-line docstring."""

__all__ = ['Shots', 'ShotInfo']


@dataclass
class ShotInfo:
    """Key information about each guess.

    Attributes:
        idx:               The index of the shot used to track.
        coord:              Grid co-ordinate of the shot.
        has_hit:            Whether the shot hit an enemy ship.
    """
    model_config = ConfigDict(validate_assignment=True)

    coord: Coord
    has_hit: Optional[bool] = None

    @field_validator('coord', mode='before')
    @classmethod
    def _validate_coord(cls, v: Any) -> Coord:
        """"""
        is_shot_valid, coord, err_msg = Coord.convert(v)

        if not is_shot_valid or coord is None:
            raise ValueError(f"Invalid Coord string: {v!r}{err_msg}")
        return coord

    @classmethod
    def from_shot(cls, shot: Any) -> "ShotInfo | None":
        """Register this ShotInfo."""
        is_valid, coord, err_msg = Coord.convert(shot)

        if coord is None or not is_valid:
            # Failure conditions.
            return None

        return ShotInfo(coord=coord)

