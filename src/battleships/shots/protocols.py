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
    from battleships.shots import Outcome as ShotOutcome

# Module-level constants


@runtime_checkable
class BoardProto(Protocol):

    def in_bounds(self, coord_like: Any) -> bool: ...
    def get(self, coord_like: Any) -> str: ...
    def mark_hit(self, coord_like: Any) -> None: ...
    def mark_miss(self, coord_like: Any) -> None: ...
    def is_marked(self, coord_like: Any) -> bool: ...


@runtime_checkable
class FleetProto(Protocol):
    def register_shot(self, coord_like: Any) -> tuple[
        'ShotOutcome', Optional[Any]]: ...
