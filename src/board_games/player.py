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
        src/board_games/player.py
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
from abc import ABC, abstractmethod
import random
from typing import (Any, Protocol, runtime_checkable, Optional, Sequence,
                    Iterable)

# Third-party imports
from pydantic import BaseModel, Field

# Local application imports
from .board import BoardLike
from .coordinate import Point2D, Coordinate, PointLike, CoordType, PointType
from .messages import Messages

__all__ = []


class PlayerLike(Protocol):
    name: str
    @property
    def is_still_playing(self) -> bool: ...
    def take_turn(self, opponent: 'PlayerLike') -> Any: ...
    def end_turn(self) -> None: ...


class BasePlayer(ABC, BaseModel):
    """Game-agnostic player base class.

    Has no knowledge of game-engines, -outcomes or -boards.

    Attributes:
        name: Player's username.
        id:
        board: Personal playing board.
        moves: Previous board cell events.
    """
    name: str
    id: int
    board: BoardLike
    moves: list[Coordinate] = Field(default_factory=list)

    @abstractmethod
    def is_still_playing(self) -> bool:
        """Game-defined semantics for if the player is still participating."""
        raise NotImplementedError

    @abstractmethod
    def get_action(self, opponent: 'BasePlayer') -> Any:
        """Game-specific action or command token."""
        raise NotImplementedError

    def record_move(self, move: Coordinate) -> None:
        self.moves.append(move)

    def on_result(self, result: Any, opponent: 'BasePlayer') -> None:
        """Optional hook to emit to UI."""
        return

    @abstractmethod
    def end_turn(self) -> None:
        """Final events before ending the turn.

        Normally involves a blocking event for humans and no-op for AIs.
        """
        raise NotImplementedError


class BaseHumanPlayer(ABC, BasePlayer):
    """Generic human player."""
    @staticmethod
    def end_turn() -> None:
        try:
            input(Messages.END_TURN)
        except EOFError:
            pass


class BaseAIPlayer(BasePlayer):
    """Generic scaffolding for a computer (AI) player."""

    _tried_moves: set['Point2D'] = Field(default_factory=set, init=False, repr=False)
    _queued_moves: list['Point2D'] = Field(default_factory=list, init=False, repr=False)

    def end_turn(self) -> None:
        """Non-blocking messages to console."""
        print('\n' + Messages.AI_END_TURN, end='\n\n')

    def _is_legal(self, opponent: 'BasePlayer', point: 'PointLike') -> bool:
        """Check if `x,y` is in-bounds and not previously tried."""
        x, y = point
        return (x, y) not in self._tried_moves and opponent.board.in_bounds((x, y))

    @staticmethod
    def _nearest_neighbours(point: 'PointLike') -> list['PointType']:
        """Orthogonal Von-Neumann neighbours.

        See my micromagnetic code for explanation.
        """
        x, y = point
        return [x - 1, y,
                x + 1, y,
                x, y - 1,
                x, y + 1]

    def _enqueue_if_legal(
            self, opponent: 'BasePlayer', *, cells: Iterable['PointLike']
    ) -> None:
        """Push legal, untried cells to the front of the queue.

        Force ``cells`` to be entered as keyword to improve readability during
        calls.
        """
        seen: set[Point2D] = set(self._queued_moves)
        for c in cells:
            if c in seen:
                continue

            if self._is_legal(opponent, point=c):
                point = Point2D(*c)
                self._queued_moves.append(point)
                seen.add(point)

    def _random_untried(self, opponent: 'BasePlayer') -> 'Point2D':
        """Randomly pick an untried cell."""
        # Attempted long list-comp to see if I prefer its readability
        if len(self._tried_moves) >= opponent.board.height * opponent.board.width:
            return Point2D(0, 0)

        candidates = [(i, j)
                      for i in range(opponent.board.height)
                      for j in range(opponent.board.width)
                      if (i, j) not in self._tried]

        point = random.choice(candidates) if candidates else (0, 0)
        return Point2D(*point)

    def get_action(self, opponent: 'BasePlayer') -> Any:
        while self._queued_moves:
            point = self._queued_moves.pop(0)
            if self._is_legal(opponent, point=point):
                self._tried_moves.add(point)
                return point

        point = self._random_untried(opponent)
        self._tried_moves.add(point)
        return point
