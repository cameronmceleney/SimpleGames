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

# Standard library imports
import random
from typing import Optional, Union, TYPE_CHECKING

# Third-party imports
from pydantic import PrivateAttr

# Local application imports
import battleships.shots as shots

from .messages import (
    parse,
    Commands,
    Registry,
    make_guess_cmd, exit_cmd, help_cmd, show_opp_cmd, show_own_cmd)

from .base_player import BasePlayer, DEFAULT_PLAYER
from .messages import Message, PlayerMessages
from utils import Divider

from src.log import get_logger

if TYPE_CHECKING:
    from board_games.coordinate import coordinate_type
    from battleships.shots.info import Info

log = get_logger(__name__)

# Module-level constants

__all__ = ['DEFAULT_PLAYER', 'HumanPlayer', 'AIPlayer']


class HumanPlayer(BasePlayer):
    """Human-controlled player object.

    Contains I/O and command parsing extensions to `BasePlayer`.
    """
    # model_config = ConfigDict(validate_default=True)

    def _get_shot_input(self, opponent: 'HumanPlayer') -> Union[str, Commands]:
        """Return a raw user input OR a command.

        Render each prompt cycle so the user sees the latest board state.

        Argument:
            opponent:

        TODO:
         - Find a way to refactor 'if/elif' block into class or function within
           'gameplay/messages.py' as that feels like a more appropriate location
        """
        self._banner()
        opponent.board.show(mode='opponent')

        raw = input(make_guess_cmd())
        cmd = parse(raw)

        if cmd is Commands.EXIT:
            print(exit_cmd())
            raise SystemExit
        elif cmd is Commands.HELP:
            print(help_cmd(commands=Registry.instance().commands_list()))
            return cmd
        elif cmd is Commands.SHOW_OWN_FLEET:
            print(show_own_cmd())
            self.board.show(mode='self', show_guides=True)
            return cmd
        elif cmd is Commands.SHOW_OPP_FLEET:
            print(show_opp_cmd())
            opponent.board.show(mode='opponent', show_guides=True)
            return cmd

        # Not a command so return the raw input back to `BasePlayer.take_turn`
        return raw

    def _on_outcome(
            self, info: 'Info', opponent: 'HumanPlayer', *, printable: bool
    ) -> None:
        print(info.outcome.message)

    def end_turn(self) -> None:
        input(Message.END_TURN)
        print('\n' * 2)


class AIPlayer(BasePlayer):
    """Computer-controlled player object.

    Dumb AI that uses random selection to make guesses.

    **Strategy**

    - Always guess a new cell by avoiding repeating past guesses.
    - After first HIT
        - if not `ship_sunk`, randomly select one of the 4 neighbouring cells.
        - if >=2 aligned hits of same ship then randomly select along that line.
        - after receiving signal `ship_sunk` clear that ship's targeting context.

    Attributes:
        _tried: Lightweight set of previous coordinates (in tuple form)

    TODO:
     - Add logic so that the AI places their own ships.
    """
    _tried: set['coordinate_type'] = PrivateAttr(default_factory=set)
    _hunt_queue: list['coordinate_type'] = PrivateAttr(default_factory=list)
    _hits_by_ship: dict[str, set['coordinate_type']] = PrivateAttr(default_factory=dict)

    def _get_shot_input(self, opponent: 'BasePlayer') -> Union[str, Commands]:
        """Return a coord-like string `x,y` for the next shot.

        Tries to use a queued target before randomly guessing a new cell.
        """
        while self._hunt_queue:
            x, y = self._hunt_queue.pop(0)
            if self._is_legal(opponent, x, y):
                self._tried.add((x, y))
                return f"{x},{y}"

        x, y = self._random_untried(opponent)
        self._tried.add((x, y))
        return f"{x},{y}"

    def _print_outcome(self, opponent: 'BasePlayer', info: 'Info', *, x: int, y: int):
        """Print messages summarising the turn.

        Keywords for ``x`` and ``y`` to ensure they're passed intentionally.

        Order of messages:
            1. Banner
            2. Guessed co-ordinate
            3. `Outcome` message
            4. Player's fleet view (visual summary)
            5. 'Turn complete' message
        """
        PlayerMessages.banner(self.name)
        print(f">>> Guessed the co-ordinates: {x}, {y}")   # TODO: Turn into a `Message`
        print(info.outcome.message)

        print('\n' + show_own_cmd())
        opponent.board.show(mode='self', show_guides=True)

    def _on_outcome(
            self, info: 'Info', opponent: 'BasePlayer', *, printable: bool
    ) -> None:
        """Update internal state and present AI's turn to the other player."""
        coord = info.coord
        self._tried.add(coord.as_tuple())

        self._print_outcome(opponent, info, x=coord.x, y=coord.y)

        if info.outcome is not shots.Outcome.HIT:
            # Early guard prevents repeating a previous guess
            return

        # Structure code in this way to avoid unnecessary repetition
        if info.ship_type is not None and info.ship_index is not None:
            ship_key = f"{info.ship_type}_{info.ship_index}"
            ship = opponent.fleet.ships.get(ship_key)
        else:
            ship_key = '_unknown_ship_'  # fallback
            ship = None

        hits = self._hits_by_ship.setdefault(ship_key, set())
        hits.add(coord.as_tuple())

        # Check sunk and clean up
        if ship is not None and ship.is_sunk:
            # Clear targeting context and queued targets for this ship
            self._hits_by_ship.pop(ship_key, None)
            self._purge_queue_around(hits)
            return

        # Managed a hit but ship not sunk, so determine next guess.
        self._enqueue_targets(opponent, ship_key)
        return

    def end_turn(self) -> None:
        """Non-blocking messages to console."""
        print('\n' + Message.AI_END_TURN, end='\n\n')

    def _is_legal(self, opponent: 'BasePlayer', x: int, y: int) -> bool:
        """Check if `x,y` is in-bounds and not previously tried."""
        # Make use of existing in_bounds() method
        return (x, y) not in self._tried and opponent.board.in_bounds((x, y))

    def _random_untried(self, opponent: 'BasePlayer') -> 'coordinate_type':
        """Randomly pick an untried cell."""
        # Attempted long list-comp to see if I prefer its readability
        candidates = [(i, j)
                      for i in range(opponent.board.height)
                      for j in range(opponent.board.width)
                      if (i, j) not in self._tried]

        return random.choice(candidates) if candidates else (0, 0)

    @staticmethod
    def _nearest_neighbours(x: int, y: int) -> list['coordinate_type']:
        """Orthogonal Von-Neumann neighbours.

        See my micromagnetic code for explanation.
        """
        return [(x - 1, y),
                (x + 1, y),
                (x, y - 1),
                (x, y + 1)]

    def _enqueue_if_legal(
            self, opponent: 'BasePlayer', *, cells: list['coordinate_type']
    ) -> None:
        """Push legal, untried cells to the front of the queue.

        Force ``cells`` to be entered as keyword to improve readability during
        calls.
        """
        seen = set(self._hunt_queue)
        for c in cells:
            if c in seen:
                continue

            if self._is_legal(opponent, *c):
                self._hunt_queue.append(c)
                seen.add(c)

    def _purge_queue_around(self, hits: set['coordinate_type']) -> None:
        """Remove queued cells that lie adjacent to a sunk ship.

        Keeps everything without bias.

        TODO:
         - Drop cells immediately adjacent to `hits` to bias elsewhere.
        """
        if not self._hunt_queue or not hits:
            return

        pruned: list['coordinate_type'] = []
        for c in self._hunt_queue:
            pruned.append(c)
        self._hunt_queue = pruned

    def _enqueue_targets(self, opponent: 'BasePlayer', ship_key: str) -> None:
        """Insert next best targets based on current hits on a ship."""
        hits = sorted(self._hits_by_ship.get(ship_key, set()))
        if not hits:
            return

        # Only one hit so pick one of four nearest neighbours
        if len(hits) == 1:
            # Prefer `*hits[0]` to `(x, y) = hits[0]` to avoid casting and initialisations
            self._enqueue_if_legal(opponent,
                                   cells=self._nearest_neighbours(*hits[0]))
            return

        # >= 2 hits so pick one of two cells along that vector
        same_row = {}
        same_col = {}
        for x, y in hits:
            same_row.setdefault(x, []).append((x, y))
            same_col.setdefault(y, []).append((x, y))

        # Prefer the alignment with >= 2 cells
        aligned: Optional[tuple[str, list['coordinate_type']]] = None
        for x, cells in same_row.items():
            # Turn if statement into helper function
            if len(cells) >= 2:
                # Sort by `y` along row
                cells.sort(key=lambda c: c[1])
                aligned = ('row', cells)
                break

            if aligned is None:
                for y, cells in same_col.items():
                    if len(cells) >= 2:
                        cells.sort(key=lambda c: c[0])
                        aligned = ('col', cells)
                        break

            # No clear alignment yet, so pick one of 4 neighbours around most
            # recent hit
            if aligned is None:
                self._enqueue_if_legal(opponent,
                                       cells=self._nearest_neighbours(*hits[-1]))
                return

            mode, cells = aligned
            first, last = cells[0], cells[-1]

            # Turn each if block into helper function
            if mode == 'row':
                x = first[0]
                y_left = first[1] - 1
                y_right = last[1] + 1
                candidates = [(x, y_left), (x, y_right)]
            else:
                y = first[1]
                x_up = first[0] - 1
                x_down = last[0] + 1
                candidates = [(x_up, y), (x_down, y)]

            self._enqueue_if_legal(opponent, cells=candidates)
            return
