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
from typing import Any, Callable, Optional, Protocol, Sequence

from battleships.gameplay import Game
from .conditions import last_playing_standing
# Third-party imports


# Local application imports
from .player import PlayerLike
from .turns import RoundRobin


class BaseGame:
    """Engine-only.

    Doesn't contain any I/O or game-specific rules.

    Attributes:
        players:
        turns:
        emit:
    """

    def __init__(self, *,
                 emitter: Optional[Callable[[str], None]] = None) -> None:
        self.players: list[PlayerLike] = []  # Need list, and not set, for __getitem__
        self.turns = RoundRobin()
        self.emit = emitter or (lambda _: None)

    def add_players(self, *players: PlayerLike) -> None:
        self.players.extend(players)
        # TODO: change next line to make better use of RoundRobin methods
        self.turns.seed(i for i, player in enumerate(players)
                        if player.is_still_playing)

    def pick_opponent(self, own_idx: int) -> Optional[int]:
        ids = self.turns.alive_of(own_idx,
                                  lambda i: self.players[i].is_still_playing)
        return ids[0] if ids else None

    def winner(self) -> Optional[int]:
        return last_playing_standing(range(len(self.players)),
                                     lambda i: self.players[i].is_still_playing)

    def play(self):

        if len(self.players) < 2:
            self.emit("Need at least two players to play game")
            return None

        if self.turns.current() is None:
            # TODO: change next line to make better use of RoundRobin methods
            self.turns.seed(i for i, player in enumerate(self.players)
                            if player.is_still_playing)

        # TODO: separate `play_loop` into several smaller methods (perhaps with private helpers)
        while True:
            winner = self.winner()
            if winner is not None:
                self.emit(f"Winner: {self.players[winner].name}")
                return winner

            if len(self.turns) <= 1:
                current_player = self.turns.current()
                if current_player is not None:
                    self.emit(f"Winner: {self.players[current_player].name}")
                    return current_player

                self.emit(f"No winner. Tie?")
                return None

            me_idx = self.turns.current()
            if me_idx is None:
                return None

            me = self.players[me_idx]
            if not me.is_still_playing:
                self.turns.remove(me_idx)
                continue

            opponent = self.pick_opponent(me_idx)
            if opponent is None:
                self.emit(f"Winner: {me.name}")
                return me

            outcome = me.take_turn(self.players[opponent])
            me.end_turn()

            if not self.players[opponent].is_still_playing:
                self.turns.remove(opponent)

            self.turns.advance()
