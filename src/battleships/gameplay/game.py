#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file game.py)

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
        src/battleships/game.py
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
from battleships.board import Board
from .player import Player, DEFAULT_PLAYER

from src.log import get_logger
log = get_logger(__name__)


class Game:
    """High-level game coordinator for Battleships.

    Allows one to play a game of battleships!

    Attributes:
        players:
        board: Shared template but each Player owns their own instance.
    """
    players: list[Player]
    board: Board

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

        # Hold a template to display at the start of the game
        self.board = Board(*board_size)

        if players_names:
            self.add_players(*players_names)

        if autoplay:
            self.board.show()
            return

    def add_players(self, *names: str) -> None:
        """Add a player to the game."""
        for n in names:
            p = self._create_player(n)
            self.players.append(p)

        self.remaining_players = len(self.players)

    def _create_player(
            self,
            name: str,
            config_file: str | None = None,
            board: Optional[Board] = None,
    ) -> Player:
        """"""
        name_ = name.capitalize()
        player_id = len(self.players)

        player = Player(
            name=name_,
            id=player_id,
            board=board or Board(height=self.board.height, width=self.board.width),

        )
        log.debug(player)

        try:
            player.apply_positions(config_file or DEFAULT_PLAYER)
        except Exception as e:
            raise e

        return player

    def _alive_opponents(self, idx: int) -> list[int]:
        return [i for i, p in enumerate(self.players)
                if i != idx and p.is_playing]

    def play(self) -> None:
        """Play a game of battleships.

        Turn-based game of battleships. Each player gets to take one shot (make
        a guess) at the enemy's position.
        """
        if len(self.players) < 2:
            # TODO. Add ability to play against random choice
            print('Need at least two players.')
            return

        while True:
            current_player = self.players[self._current_player_idx]
            if not current_player.is_playing:
                self._current_player_idx = (self._current_player_idx + 1) % len(self.players)
                continue

            opp_indices = self._alive_opponents(self._current_player_idx)
            if not opp_indices:
                # No more opponents means this player won
                print(f'Winner: {current_player.name}')
                break

            opponent = self.players[opp_indices[0]]
            _ = current_player.take_turn(opponent=opponent)
            Player.end_turn()

            if not opponent.is_playing:
                print(f"{opponent.name} has been eliminated!")

            self._current_player_idx = (self._current_player_idx + 1) % len(self.players)


def test_battleships() -> None:
    bs = Game(board_size=(5, 5), autoplay=False)
    bs.add_players("cameron", "karolina")
    # print(f"Players\n{bs.players}")
    bs.play()


if __name__ == '__main__':
    test_battleships()
