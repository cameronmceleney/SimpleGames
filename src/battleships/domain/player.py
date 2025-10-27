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

from functools import cached_property

# Standard library imports
import os
import platform
from pydantic import BaseModel, ConfigDict, Field, model_validator
from typing import Any

# Third-party imports

# Local application imports
from src.battleships.domain.fleet import Fleet
from src.battleships.domain.board import Board
from src.utils.utils import JustifyText, Divider, load_yaml
from src.battleships.domain.coordinate import Coordinate

# Module-level constants
PLAYER_FILE_PATH = "config/player.yml"

from src.log import get_logger

log = get_logger(__name__)

__all__ = ['Player', 'MESSAGES']

MESSAGES: dict = {
    'make_guess': "Enter the co-ordinates of your next shot: "
}


class Player(BaseModel):
    """Define player.

    Attributes:
        name:           Player's name

        board:          2D grid showing their ships.

        fleet:          All ships and their positions.

        shots:          All guessed shots made by the player
    """
    name: str
    id: int

    fleet: Fleet = Field(default_factory=lambda: Player._default_fleet())
    board: Board = Field(default_factory=lambda: Player._default_board())
    shots: list[Coordinate] = Field(default_factory=list)

    _config_file: str | None = None

    @property
    def is_playing(self) -> bool:
        return self.fleet.is_alive

    @staticmethod
    def _default_fleet() -> Fleet:
        return Fleet.load_from_yaml(fleet_id='basic_fleet_1')

    @staticmethod
    def _default_board() -> Board:
        return Board(length=6, width=6)

    def apply_positions(self, filepath: str | None) -> None:
        """"""
        player_data = load_yaml(filepath or PLAYER_FILE_PATH)
        log.debug(player_data)
        self.fleet.apply_player_positions(player_data)
        # self.shots
        self.board.add_ship(*self.fleet.ships.values())

    def take_turn(self):
        """"""
        player_input = self._get_shot()
        self._take_shot()

    def _get_shot(self):
        """"""
        msg = f"<Player {self.id}> {MESSAGES['make_guess']} "
        player_input = input(msg)

    def _take_shot(self) -> None:
        """"""
        msg = f"<Player {self.id}> {MESSAGES['make_guess']} "
        player_input = input(msg)
        shot, err_msg = self.board.add_shot(player_input)
        if err_msg is None:
            self.shots.append(shot)

        return

    @classmethod
    def end_turn(cls):
        print("\n" * 4)

    def __str__(self, print_headers: bool = True):

        msg = ""
        if print_headers:
            msg += f"{CONSOLE_DIVIDER}"

        msg += f"<Player> '{self.name}'\n"
        msg += f"{CONSOLE_DIVIDER}"
        msg += self.fleet.__str__(print_headers=False)
        msg += f"{CONSOLE_DIVIDER}"
        msg += self.board.__str__(print_headers=False)

        if print_headers:
            msg += f"{CONSOLE_DIVIDER}"

        return msg
