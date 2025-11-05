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
from typing import Any, Iterable, Protocol, TYPE_CHECKING

# Third-party imports
from pydantic import BaseModel, ConfigDict, PrivateAttr

# Local application imports
from .messages import Messages
from board_games.board import BoardLike
from board_games.coordinate import Coordinate

if TYPE_CHECKING:
    from board_games.coordinate import CoordType, CoordLike


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
        _moves: Previous board cell events.
    """
    model_config = ConfigDict(arbitrary_types_allowed=True, validate_default=True)

    name: str
    id: int
    board: BoardLike

    _moves: list[Coordinate] = PrivateAttr(default_factory=list)

    @property
    @abstractmethod
    def is_still_playing(self) -> bool:
        """Game-defined semantics for if the player is still participating."""
        raise NotImplementedError

    @abstractmethod
    def get_action(self, opponent: Any) -> Any:
        """Game-specific action or command token."""
        raise NotImplementedError

    def record_move(self, move: 'CoordLike') -> None:
        """Store player's move."""
        c = Coordinate.coerce(move)
        self._moves.append(c)

    @abstractmethod
    def on_result(self, opponent: Any, result: Any) -> Any:
        """Optional hook to emit to the user-interface."""
        raise NotImplementedError

    @abstractmethod
    def take_turn(self, opponent: Any) -> Any:
        """Orchestrator for a single turn.

        Shared flow that delegates to optional overloaded methods for input.
        Overloaded method may support I/O.

        Arguments:
            opponent: Opposing entity/entities that this player's turn involves.
        """
        raise NotImplementedError

    @abstractmethod
    def end_turn(self) -> Any:
        """Final events before ending the turn.

        Normally involves a blocking event for humans and no-op for AIs.
        """
        raise NotImplementedError


class BaseHumanPlayer(BasePlayer, ABC):
    """Generic human player."""

    def end_turn(self) -> None:
        try:
            input(Messages.END_TURN)
        except EOFError:
            pass
        else:
            return


class BaseAIPlayer(BasePlayer, ABC):
    """Generic scaffolding for a computer (AI) player.

    Attributes:
        _queued_moves: Stored moves to attempt sequentially in upcoming turns.
        _tried_index: Completed moves from previous turns.
    """
    _queued_moves: list[Coordinate] = PrivateAttr(default_factory=list)
    _tried_index: set['CoordType'] = PrivateAttr(default_factory=set)

    def end_turn(self) -> None:
        """Non-blocking final events before ending turn.

        Note:
            Don't decorate this method with `@staticmethod` as it conflicts
            with `BasePlayer.end_turn()`.
        """
        print('\n' + Messages.AI_END_TURN, end='\n\n')
        return

    def _is_legal(self, opponent: BasePlayer, coord: Coordinate) -> bool:
        """Check if `x,y` is in-bounds and not previously tried."""
        return (coord not in self._tried_index) and opponent.board.in_bounds(coord)

    @staticmethod
    def _nearest_neighbours(coord: Coordinate) -> list[Coordinate]:
        """Orthogonal Von-Neumann neighbours.

        See my micromagnetic code for explanation.
        """
        neighbours: list['CoordType'] = [
            (coord.x - 1, coord.y),
            (coord.x + 1, coord.y),
            (coord.x, coord.y - 1),
            (coord.x, coord.y + 1)
        ]
        return [Coordinate.from_xy(n) for n in neighbours]

    def _enqueue_if_legal(
            self, opponent: BasePlayer, cells: Iterable['CoordLike']
    ) -> None:
        """Push legal, untried cells to the front of the queue.

        Force ``cells`` to be entered as keyword to improve readability during
        calls.
        """
        seen: set['CoordType'] = {c.as_xy() for c in self._queued_moves}
        for c in cells:
            coord = Coordinate.coerce(c)
            if coord.as_xy() in seen:
                continue

            if self._is_legal(opponent, c):
                self._queued_moves.append(coord)
                seen.add(coord.as_xy())

    def _random_untried(self, opponent: BasePlayer) -> Coordinate:
        """Randomly pick an untried cell."""
        # Attempted long list-comp to see if I prefer its readability
        if len(self._tried_index) >= opponent.board.height * opponent.board.width:
            return Coordinate(0, 0)

        candidates = [Coordinate(i, j)
                      for i in range(opponent.board.height)
                      for j in range(opponent.board.width)
                      if Coordinate(i, j) not in self._tried_index]

        point = random.choice(candidates) if candidates else (0, 0)
        return Coordinate.from_xy(point)

    def get_action(self, opponent: BasePlayer) -> Coordinate:
        """Default action source: queue first, otherwise get new.

        Overload in concrete instance as needed.
        """
        while self._queued_moves:
            queued_move = self._queued_moves.pop(0)
            if self._is_legal(opponent, queued_move):
                self._tried_index.add(queued_move.as_xy())
                return queued_move

        new_move = self._random_untried(opponent)
        self._tried_index.add(new_move.as_xy())
        return new_move

    def record_move(self, move: 'CoordLike') -> None:
        super().record_move(move)
        self._tried_index.add(Coordinate.coerce(move).as_xy())
