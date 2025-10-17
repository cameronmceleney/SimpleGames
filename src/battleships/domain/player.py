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

from wsgiref import headers

# Standard library imports
from pydantic import BaseModel, ConfigDict, Field
from dataclasses import dataclass, field

# Third-party imports

# Local application imports
from src.battleships.domain.fleet import Fleet
from src.battleships.domain.board import Board
from src.utils.utils import JUST_L_WIDTH, CONSOLE_DIVIDER

# Module-level constants

__all__ = ['Player']


@dataclass
class Player:
    """Define player.

    Attributes:
        name:           Player's name

        board:          2D grid showing their ships.

        fleet:          All ships and their positions.

        shots:          All guessed shots made by the player
    """
    name: str
    fleet: Fleet | None = None
    board: Board | None = None
    shots: list[tuple[int, int]] = field(default_factory=list)

    def __str__(self, headers: bool = True):

        msg = ""
        if headers:
            msg += f"{CONSOLE_DIVIDER}"

        msg += f"<Player> '{self.name}'\n"
        msg += f"{CONSOLE_DIVIDER}"
        msg += self.fleet.__str__(headers=False)
        msg += f"{CONSOLE_DIVIDER}"
        msg += self.board.__str__(headers=False)

        if headers:
            msg += f"{CONSOLE_DIVIDER}"

        return msg
