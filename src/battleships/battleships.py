#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file battleships.py)

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
        src/battleships/battleships.py
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
from typing import Optional

# Third-party imports

# Local application imports
from src.battleships.domain.board import BattleshipBoard as Board
from src.battleships.domain.player import (
    Player,
    MESSAGES as PLAYER_MESSAGES)

from src.log import get_logger

log = get_logger(__name__)

# Module-level constants

__all__ = ['Battleships']


class Battleships:
    """Battleships class.

    Allows one to play a game of battleships!

    Attributes:
        players:            All players in the game.
    """
    players: list[Player]
    board: Board

    _rosters_yaml = "config/rosters.yml"

    def __init__(
            self,
            board_size: tuple[int, int] = (10, 10),
            *,
            players_names: Optional[list[str]] = None,
            autoplay: bool = True
    ):
        """"""
        self.players = []
        self.remaining_players: int = 0
        self._current_player_idx: int = 0
        self._current_player: Optional[Player] = None

        self.board = Board(*board_size)

        if players_names is not None:
            self.add_players(*players_names)

        self._post_init(autoplay=autoplay)

    def _post_init(self, **kwargs):
        if 'autoplay' in kwargs.keys() and kwargs['autoplay']:
            print("Working autoplay.")
            self.board.show()
            exit(0)

    def add_players(self, *names: str) -> None:
        """Add a player to the game."""
        for n in names:
            self.players.append(self._create_player(n))

            if len(self.players) == 1:
                self._current_player = self.players[0]

    def _create_player(self, name: str) -> Player:
        """"""
        name_ = name.capitalize()
        id_ = len(self.players)
        player = Player(name=name_, id=id_)
        log.debug(player)

        player.apply_positions('config/player.yml')

        # Update class attributes
        self.remaining_players += 1

        return player

    def play(self) -> None:
        """Play a game of battleships.

        Turn-based game of battleships. Each player gets to take one shot (make
        a guess) at the enemy's position.
        """
        while self.remaining_players > 1:
            self._current_player.take_turn()
            Player.end_turn()

    def _allow_guess(self, idx: int):
        """"""
        msg = f"<Player {idx}> {PLAYER_MESSAGES['make_guess']} "
        player_input = input(msg)
        print(player_input)


def _test_battleships() -> None:
    bs = Battleships(board_size=(4, 4), autoplay=False)
    bs.add_players("cameron", "karolina")
    # print(f"Players\n{bs.players}")
    bs.play()


if __name__ == '__main__':
    _test_battleships()
