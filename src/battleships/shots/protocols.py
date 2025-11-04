#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file protocols.py)

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
from typing import (
    Any,
    Optional,
    Protocol, runtime_checkable,
    TYPE_CHECKING
)

# Third-party imports

# Local application imports
if TYPE_CHECKING:
    from battleships.shots import Outcome
    from battleships.ships import Ship
    from board_games.coordinate import CoordLike

# Module-level constants


@runtime_checkable
class BoardProto(Protocol):

    def in_bounds(self, coord_like: CoordLike) -> bool: ...
    def get(self, coord_like: CoordLike) -> str: ...
    def mark_hit(self, coord_like: CoordLike) -> None: ...
    def mark_miss(self, coord_like: CoordLike) -> None: ...
    def is_marked(self, coord_like: CoordLike) -> bool: ...


@runtime_checkable
class FleetProto(Protocol):
    def apply_shot(self, coord_like: CoordLike) -> tuple[Outcome, Optional[Ship]]: ...
