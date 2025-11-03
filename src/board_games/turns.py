#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file turns.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of turns.py). Note that leading symbol '>>>' includes the 
    code in doctests, while '$' does not.)::
        
        >>> bar = 1
        >>> foo = bar + 1

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
        src/board_games/turns.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        03 Nov 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from abc import ABC, abstractmethod
from collections import deque
from typing import Callable, Iterable, Literal, Optional, Sequence

# Third-party imports

# Local application imports

# Module-level constants

__all__ = ['RoundRobin']


class TurnOrder(ABC):
    """Base class for mutable playing turn-order over player IDs."""
    @abstractmethod
    def seed(self, ids: Iterable[int]) -> None:
        """Seeds the turn order.

        Arguments:
            ids: Player IDs
        """
        ...

    @property
    @abstractmethod
    def playing_order(self) -> Optional[Sequence[int]]:
        """Current playing order/rotation."""
        ...

    @abstractmethod
    def current(self) -> Optional[int]:
        """Index of the current player."""
        ...

    @abstractmethod
    def next(self) -> Optional[int]:
        """Index of the next player."""
        ...

    @abstractmethod
    def advance(self) -> Optional[int]:
        """Increment the turn order."""
        ...

    @abstractmethod
    def remove(self, pid: int) -> None:
        """Remove a player from the turn order.

        If removing current, then the next player becomes current to ensure
        stability of the iterator.

        Arguments:
            pid: Player ID.
        """

    @abstractmethod
    def __len__(self) -> int: ...

    def has_winner(self) -> bool:
        return len(self) <= 1


class RoundRobin(TurnOrder):
    """Each player plays against their neighbour to the right.

    Attributes:
        playing_order: Current playing order.
    """

    def __init__(
            self, ids: Iterable[int] = (), *,
            direction: Literal['left', 'right'] = 'left'):
        self._dq: deque[int] = deque()
        self._dir: int = -1 if direction == 'left' else 1
        self.seed(ids)

    def seed(self, ids: Iterable[int]) -> None:
        seen: set[int] = set()
        unique_ids: list[int] = []
        for i in ids:
            i = int(i)
            if i not in seen:
                seen.add(i)
                unique_ids.append(i)

        self._dq = deque(unique_ids)

    @property
    def playing_order(self) -> Optional[Sequence[int]]:
        """Current playing order/rotation."""
        return tuple(self._dq) if self._dq else None

    def current(self) -> int | None:
        return self._dq[0] if self._dq else None

    def next(self) -> Optional[int]:
        if not self._dq:
            return None

        if len(self._dq) == 1:
            return self._dq[0]
        # Peak without mutating the deque, and respecting chosen direction
        return self._dq[self._dir]

    def advance(self) -> Optional[int]:
        if not self._dq:
            return None
        self._dq.rotate(self._dir)
        return self._dq[0]

    def remove(self, pid: int) -> None:
        if not self._dq:
            return None

        try:
            self._dq.remove(pid)
        except ValueError:
            pass

    def alive_of(self, me: int, is_alive: Callable[[int], bool]) -> list[int]:
        """The other surviving players (opponents) in playing order."""
        return [i for i in self._dq if i != me and is_alive(i)]

    def remove_defeated(self, is_alive: Callable[[int], bool]) -> None:
        """Strip all defeated players from the turn order."""
        if not self._dq:
            return

        cur = self._dq[0]
        kept = [pid for pid in self._dq if is_alive(pid)]
        self.seed(kept)

        if cur in self._dq:
            while self._dq and self._dq[0] != cur:
                self._dq.rotate(self._dir)

    def __len__(self) -> int:
        return len(self._dq)

    def __bool__(self) -> bool:
        return bool(self._dq)
