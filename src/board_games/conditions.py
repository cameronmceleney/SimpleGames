#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file conditions.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of conditions.py). Note that leading symbol '>>>' includes the 
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
        src/board_games/conditions.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        03 Nov 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from typing import Sequence, Protocol

# Third-party imports

# Local application imports

# Module-level constants


class AliveQuery(Protocol):
    """Check if an entity is still alive in the game.

    Querying this is equivalent to asking 'are they still playing?'.
    """
    def __call__(self, pid: int) -> bool: ...


def last_playing_standing(
        player_ids: Sequence[int], is_alive: AliveQuery
) -> int | None:
    alive = [pid for pid in player_ids if is_alive(pid)]
    return alive[0] if len(alive) == 1 else None
