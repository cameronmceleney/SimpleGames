#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file player.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)

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
        src/battleships/player.py
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
from pydantic import BaseModel, ConfigDict, Field

# Third-party imports

# Local application imports
from src.battleships.domain.fleet import Fleet
from src.battleships.domain.board import Board

# Module-level constants

__all__ = ['Player']


class Player(BaseModel):
    """"""
    model_config = ConfigDict(frozen=True, validate_default=True)

    name: str
    board: Board
    fleet: Fleet

    shots: list[]

    guesses: list[tuple[int, int]] = Field(default_factory=list)
    active_ships: list[str] = Field(default_factory=list)
    ship_positions: dict[str, tuple[int, int]] = Field(default_factory=dict)
