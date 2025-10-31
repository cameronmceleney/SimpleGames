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
from typing import Any, Optional

# Third-party imports

# Local application imports
from board_games import Coordinate
from .info import Info
from .outcome import Outcome
from .protocols import BoardProto, FleetProto

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
    def process(target_board: BoardProto,
                target_fleet: FleetProto,
                shot_like: Any) -> Info:
        """Proceedings.

        Order of checks:
        1. coerce -> INVALID
        2. in_bounds -> OUT
        3. board cell repeat -> REPEAT
        4. fleet.register_shot -> HIT/MISS
        """
        coord, err = Engine.coerce(shot_like)
        if coord is None:
            return Info(coord=Coordinate(0, 0),
                        outcome=Outcome.INVALID)

        if not target_board.in_bounds(coord):
            return Info(coord=coord,
                        outcome=Outcome.OUT)

        if (getattr(target_board, 'is_marked', None)
                and target_board.is_marked(coord)):
            return Info(coord=coord, outcome=Outcome.REPEAT, repeat=True)

        outcome, ship = target_fleet.register_shot(coord)
        if outcome is Outcome.MISS:
            target_board.mark_miss(coord)
            return Info(coord=coord, outcome=Outcome.MISS)

        if outcome is Outcome.HIT:
            target_board.mark_hit(coord)
            return Info(coord=coord, outcome=Outcome.HIT,
                        ship_type=getattr(ship, 'type', None),
                        ship_index=getattr(ship, 'index', None))

        return Info(coord=coord, outcome=outcome or Outcome.ERROR)
