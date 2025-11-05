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
        src/board_games/game.py
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
from typing import Callable, Optional, TYPE_CHECKING

# Third-party imports


# Local application imports
from .turns import RoundRobin

if TYPE_CHECKING:
    from board_games.player import PlayerLike

__all__ = ['BaseGame']


class BaseGame:
    """Engine-only orchestator.

    Doesn't contain any I/O or game-specific rules.

    Attributes:
        players:
        turns:
        emit:

    TODO:
     - Change `self.turns` to be initialised generic TurnOrder, not always
       RoundRobin.
    """

    def __init__(self, *,
                 emitter: Optional[Callable[[str], None]] = None) -> None:
        self.players: list[PlayerLike] = []  # Need list, and not set, for __getitem__
        self.turns = RoundRobin()
        self.emit = emitter or (lambda _: None)

    @property
    def remaining_players(self) -> int:
        """Players still in the game."""
        return sum(1 for player in self.players if player.is_still_playing)

    @property
    def current_player_index(self) -> Optional[int]:
        return self.turns.current()

    @property
    def current_player(self) -> Optional[PlayerLike]:
        idx = self.turns.current()
        return None if idx is None else self.players[idx]

    def _reseed_turns(self) -> None:
        self.turns.seed(
            i for i, player in enumerate(self.players)
            if player.is_still_playing
        )

    def add_players(self, *players: PlayerLike) -> None:
        self.players.extend(players)
        self._reseed_turns()

    def pick_opponent(self, own_idx: int) -> Optional[int]:
        ids = self.turns.alive_of(own_idx,
                                  lambda i: self.players[i].is_still_playing)
        return ids[0] if ids else None

    def winner(self) -> Optional[int]:
        self.turns.remove_defeated(lambda i: self.players[i].is_still_playing)
        return self.turns.current() if self.turns.has_winner() else None

    def play(self):
        if len(self.players) < 2:
            self.emit("Need at least two players to play game")
            return None

        if self.turns.current() is None:
            self._reseed_turns()

        while True:
            # Start the turn
            self.turns.remove_defeated(lambda i: self.players[i].is_still_playing)

            # Check for winner
            winner = self.winner()
            if winner is not None:
                self.emit(f"Winner: {self.players[winner].name}")
                return winner

            # Check for draw
            me_idx = self.turns.current()
            if me_idx is None:
                self.emit("No more players or a winner. Tie?")
                return None

            # Check if the player themself are still in the game
            me = self.players[me_idx]
            if not me.is_still_playing:
                self.turns.remove(me_idx)
                continue

            # Identify opponent
            opponent_idx = self.pick_opponent(me_idx)
            if opponent_idx is None:
                self.emit(f"Winner: {me.name}")
                return me_idx

            # Process one full turn for the player
            opponent = self.players[opponent_idx]
            _ = me.take_turn(opponent)
            me.end_turn()
            if not opponent.is_still_playing:
                self.turns.remove(opponent_idx)

            self.turns.advance()
