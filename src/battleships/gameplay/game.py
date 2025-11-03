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
from collections import deque, Counter
from typing import Iterable, Literal, Optional

# Third-party imports
from namedlist import namedlist

# Local application imports
from battleships.board import Board
from .base_player import BasePlayer
from .player import DEFAULT_PLAYER, AIPlayer, HumanPlayer
from.messages import Message

from src.log import get_logger
log = get_logger(__name__)


class Game:
    """High-level game coordinator for Battleships.

    Allows one to play a game of battleships!

    Attributes:
        players:
        board: Shared template used to create each player.
        _playing_order: Indices of the players that are still alive.

    Each player owns their own table-top instances such as `Board` and `Fleet`.
    """
    players: list[BasePlayer]
    board: Board

    _playing_order: deque[int]


    def __init__(
            self,
            board_size: tuple[int, int] = (10, 10),
            *,
            players_names: Optional[list[str]] = None,
            autoplay: bool = True
    ):
        """

        Arguments:
            board_size:
            players_names:
            autoplay:
        """
        self.players: list[BasePlayer] = []
        self._playing_order: deque[int] = deque()
        self.board = Board(*board_size)

        if players_names:
            self.add_players(*players_names)

        if autoplay:
            self.board.show()

    @property
    def remaining_players(self, category: Literal['human', 'ai', 'both'] = 'both') -> int:
        """Number of players remaining."""
        remaining = Counter()

        for p in self.players:
            match p:
                case HumanPlayer():
                    remaining['human'] += 1
                case AIPlayer():
                    remaining['ai'] += 1

        return remaining.total() if category == 'both' else remaining[category]

    @property
    def current_player_index(self) -> int:
        return self._playing_order[0] if self._playing_order else -1

    @property
    def current_player(self) -> BasePlayer:
        return self.players[self.current_player_index]

    def _next_player(self) -> None:
        if self._playing_order:
            self._playing_order.rotate(-1)

    def _create_human_player(
            self,
            name: str,
            config_file: str | None = None,
            board: Optional[Board] = None,
    ) -> HumanPlayer:
        """"""
        player = HumanPlayer(
            name=name.capitalize(),
            id=len(self.players),
            board=board or Board(height=self.board.height, width=self.board.width),

        )
        log.debug(player)

        try:
            player.apply_positions(config_file or DEFAULT_PLAYER)
        except Exception as e:
            raise e

        return player

    def _create_ai_player(self, name: str = "CPU", suffix: str = '') -> AIPlayer:
        """Small helper to add AI players to a game.
        """
        p = AIPlayer(
            name=f'{name}_{suffix}',
            id=len(self.players)
        )
        p.apply_positions(DEFAULT_PLAYER)
        return p

    def add_players(self, *names: str, num_ai: int = 0) -> None:
        """Add a player to the game."""
        for n in names:
            p = self._create_human_player(n)
            self.players.append(p)

        for i in range(num_ai):
            p = self._create_ai_player(suffix=str(i))
            self.players.append(p)

        self._reseed_playing_order()

    def _reseed_playing_order(self) -> None:
        self._playing_order = deque(i for i, p in enumerate(self.players)
                                    if p.is_still_playing)

    def _alive_opponents_of(self, idx: int) -> list[int]:
        return [i for i in self._playing_order
                if i != idx and self.players[i].is_still_playing]

    def _remove_if_defeated(self, idx: int) -> None:
        """Remove a player index from the turn order if they've been defeated."""
        if not self.players[idx].is_still_playing:
            try:
                self._playing_order.remove(idx)
            except ValueError:
                pass

    def play(self) -> None:
        """Play a game of battleships.

        Turn-based game of battleships. Each player gets to take one shot (make
        a guess) at the enemy's position.
        """
        if len(self.players) < 2:
            print('Need at least two players.')
            return

        if not self._playing_order:
            self._reseed_playing_order()

        while True:
            if len(self._playing_order) <= 1:
                print(Message.WINNER
                      if self._playing_order
                      else Message.KEEP_PLAYING)
                break

            if not self.current_player.is_still_playing:
                self._remove_if_defeated(self.current_player_index)
                continue

            opp_indices = self._alive_opponents_of(self.current_player_index)
            if not opp_indices:
                print(Message.WINNER)
                break

            opponent = self.players[opp_indices[0]]

            outcome = self.current_player.take_turn(opponent=opponent)
            self.current_player.end_turn()

            self._remove_if_defeated(opp_indices[0])

            self._next_player()

            #
            # current_player = self.players[self._current_player_idx]
            # if not current_player.is_still_playing:
            #     self._current_player_idx = (self._current_player_idx + 1) % len(self.players)
            #     continue
            #
            # opp_indices = self._alive_opponents(self._current_player_idx)
            # if not opp_indices:
            #     # No more opponents means this player won
            #     print(f'Winner: {current_player.name}')
            #     break
            #
            # opponent = self.players[opp_indices[0]]
            # outcome = current_player.take_turn(opponent=opponent)
            # current_player.end_turn()
            #
            # if not opponent.is_still_playing:
            #     # print(f"{opponent.name} has been eliminated!")
            #     print(Message.ELIMINATED)
            # self.players.
            #
            # self._current_player_idx = (self._current_player_idx + 1) % len(self.players)


def test_battleships() -> None:
    bs = Game(board_size=(5, 5), autoplay=False)
    bs.add_players("cameron", "karolina")
    # print(f"Players\n{bs.players}")
    bs.play()


if __name__ == '__main__':
    test_battleships()
