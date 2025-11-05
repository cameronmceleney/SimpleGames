#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file engine.py)

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
from typing import Any, Optional, TYPE_CHECKING

# Third-party imports

# Local application imports
from board_games import Coordinate
from .info import Info
from .outcome import Outcome
from .protocols import BoardLike, FleetLike

if TYPE_CHECKING:
    from board_games.coordinate import CoordLike

# Module-level constants


class Engine:
    """Pure, centralised shot rules.
    """

    @staticmethod
    def coerce(shot_like: Any) -> tuple[Optional[Coordinate], Optional[str]]:
        try:
            return Coordinate.coerce(shot_like), None
        except Exception as e:
            return None, f"{type(e).__name__}: {e}"

    @staticmethod
    def process(
            coord_like: Any,
            target_board: 'BoardLike',
            target_fleet: 'FleetLike'
    ) -> Info:
        """Determine the outcome of a shot.

        Order of checks upon a shot (Test -> result if failed)

            1. coerce -> INVALID
            2. is in bounds -> OUT
            3. (board) cell isn't marked -> REPEAT
            4. hits a ship -> MISS
            5. Return HIT
        """
        coord, err = Engine.coerce(coord_like)

        if coord is None:
            return Info(coord=Coordinate(0, 0),
                        outcome=Outcome.INVALID)

        if not target_board.in_bounds(coord):
            return Info(coord=coord,
                        outcome=Outcome.OUT)

        if (getattr(target_board, 'is_marked', None)
                and target_board.is_marked(coord)):
            return Info(coord=coord, outcome=Outcome.REPEAT, repeat=True)

        outcome, ship = target_fleet.apply_shot(coord)
        if outcome is Outcome.MISS:
            target_board.mark_miss(coord)
            return Info(coord=coord, outcome=Outcome.MISS)

        if outcome is Outcome.HIT:
            target_board.mark_hit(coord)
            return Info(coord=coord, outcome=Outcome.HIT,
                        ship_type=getattr(ship, 'type', None),
                        ship_index=getattr(ship, 'type_index', None))

        return Info(coord=coord, outcome=outcome or Outcome.ERROR)
