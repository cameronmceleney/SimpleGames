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

# Third-party imports

# Local application imports
from src.battleships.domain.board import Board
from src.battleships.domain.player import Player
from src.battleships.domain.fleet import Fleet
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
    players: dict[str, Player]
    _board_size: tuple[int, int]

    def __init__(
            self,
            board_size: tuple[int, int] = (10, 10),
            autoplay: bool = True
    ):
        """"""
        self.players = {}
        self._board_size = board_size
        self._rosters_yaml = "config/rosters.yml"

        self._post_init(autoplay=autoplay)

    @staticmethod
    def _post_init(**kwargs):
        if 'autoplay' in kwargs.keys() and kwargs['autoplay'] == True:
            print("Working autoplay.")
            board = Board(length=5, width=5)
            board.show()

            exit()

    def add_players(self, *names: str) -> None:
        """Add a player to the game."""
        for n in names:
            f = Fleet.load_from_yaml(fleet_id='basic_fleet_1')
            b = Board(length=self._board_size[0], width=self._board_size[1])
            p = Player(name=n, fleet=f, board=b)
            print(p.fleet.ships)

            self.players[n] = p

    def load(self):
        """Load configuration data from yaml file."""
        return

    def play(self):
        """Play a game of battleships."""
        return


if __name__ == '__main__':
    bs = Battleships(board_size=(4, 4), autoplay=False)
    bs.add_players("cameron")
    # print(f"Players\n{bs.players}")
    bs.load()
