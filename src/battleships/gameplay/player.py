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
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Literal, Optional, TypeAlias, TYPE_CHECKING

# Third-party imports
from pydantic import ConfigDict, Field, PrivateAttr

# Local application imports
from board_games.player import BasePlayer, BaseHumanPlayer, BaseAIPlayer
from board_games.coordinate import CoordType, CoordLike, Coordinate
from utils import Divider, load_yaml

import battleships.shots as shots
from battleships.board import _BoardDefaults, Board
from battleships.ships import _FleetDefaults, Fleet

from .messages import (
    parse,
    Commands,
    _is_command_token,
    Registry,
    make_guess_cmd, exit_cmd, help_cmd, show_opp_cmd, show_own_cmd)

from .messages import PlayerMessages

from src.log import get_logger

if TYPE_CHECKING:
    from battleships.shots import Info, Outcome

log = get_logger(__name__)


# Module-level constants
ROW_COL_SYMBS: TypeAlias = Literal['row', 'col']


@dataclass(frozen=True)
class _Defaults:
    """
    Attributes:
        file_path: Default relative path to a player's configuration file.
    """
    file_path: str = 'battleships/config/player.yml'


__all__ = ['_Defaults', 'HumanPlayer', 'AIPlayer']


class BaseBattleshipPlayer(BasePlayer, ABC):
    model_config = ConfigDict(validate_default=True)

    board: Board = Field(default_factory=lambda: _BoardDefaults.create_board())
    fleet: Fleet = Field(default_factory=lambda: _FleetDefaults.create_fleet())

    @property
    def is_still_playing(self) -> bool:
        return self.fleet.is_alive

    def _banner(self) -> Optional[str]:
        """Console title announcing the player."""
        # TODO: Turn below f-string into easier-to-read print format
        banner = Divider.console.make_title("Player", self.name)
        print(f"\n{banner}")
        return banner

    def apply_placements(self, filepath: Optional[str]) -> None:
        """Load ship placements and add to board.

        Arguments:
            filepath: Relative path to file containing ship placements.
        """
        data = load_yaml(filepath or _Defaults.file_path)
        log.debug(data)

        self.fleet.apply_placements(data)
        self.place_fleet()

    def place_fleet(self) -> None:
        """Place this player's fleet onto their board."""
        for ship in self.fleet.ships.values():
            if ship.placement is None:
                continue

            self.board.place(pos=ship.placement, symbol=ship.symbol or ship.spec.symbol)

    def record_shot(self, shot: 'Coordinate') -> None:
        """Alias for battleship game's clarity.
        """
        self.record_move(shot)

    @abstractmethod
    def get_action(self, opponent: BasePlayer) -> 'CoordLike' | Commands:
        """Return a coordinate-like input or a command token.

        Render each prompt cycle so the user sees the latest board state.
        """
        raise NotImplementedError

    @abstractmethod
    def on_result(self, opponent: BaseBattleshipPlayer, result: 'Info') -> None:
        """Print a summary of the shot to the console."""
        raise NotImplementedError

    def take_turn(self, opponent: BaseBattleshipPlayer) -> 'Outcome':
        """
        TODO:
         - Fix linter warning that "Expected type 'Outcome', got 'Outcome | None' instead"
           due to lack of `return` outside of `while True` block.
        """
        while True:
            raw = self.get_action(opponent)
            if raw is None:
                log.debug("`get_action()` returned None. Continuing...")
                continue

            if _is_command_token(raw):
                continue

            info = shots.Engine.process(raw, opponent.board, opponent.fleet)

            if info.outcome in shots.Outcome.failures():
                self.on_result(opponent, info)
                continue

            if info.outcome not in (shots.Outcome.INVALID, shots.Outcome.ERROR, shots.Outcome.OUT):
                self.record_shot(info.coord)
                self.on_result(opponent, info)
                return info.outcome

        raise RuntimeError("Shot did not complete and managed to break "
                           "`While True` loop.")


class HumanPlayer(BaseHumanPlayer, BaseBattleshipPlayer):

    def get_action(self, opponent):
        # TODO: Find a way to refactor 'if/elif' block into class or function
        #       within 'gameplay/messages.py' as that feels like a more
        #       appropriate location
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

    def on_result(self, opponent, result):
        print(result.outcome.message)


class AIPlayer(BaseAIPlayer, BaseBattleshipPlayer):
    """Computer-controlled player object.

    Dumb AI that uses random selection to make guesses.

    **Strategy**

    - Always guess a new cell by avoiding repeating past guesses.
    - After first HIT
        - if not `ship_sunk`, randomly select one of the 4 neighbouring cells.
        - if >=2 aligned hits of same ship then randomly select along that line.
        - after receiving signal `ship_sunk` clear that ship's targeting context.

    Attributes:
        _queued_moves: Stored moves to attempt sequentially in upcoming turns.
        _hits_by_ship: Description missing.

    TODO:
     - Add logic so that the AI places their own ships.
    """
    _hits_by_ship: dict[str, set[
        'CoordType']] = PrivateAttr(default_factory=dict)

    def _print_outcome(self, opponent: BasePlayer, result: 'Info', ) -> None:
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
        print(f">>> Guessed the co-ordinates: "
              f"{result.coord.x}, {result.coord.y}")   # TODO: Turn into a `Message`
        print(result.outcome.message)
        print('\n' + show_own_cmd())
        opponent.board.show(mode='self', show_guides=True)

    def on_result(self, opponent, result):
        self.record_shot(result.coord)
        self._print_outcome(opponent, result)

        if result.outcome is not shots.Outcome.HIT:
            return

        # Structure code in this way to avoid unnecessary repetition
        if result.ship_type is not None and result.ship_index is not None:
            ship_key = f"{result.ship_type}_{result.ship_index}"
            ship = opponent.fleet.ships.get(ship_key)
        else:
            ship_key = '_unknown_ship_'  # fallback
            ship = None

        hits = self._hits_by_ship.setdefault(ship_key, set())
        hits.add(result.coord.as_xy())

        if ship is not None and ship.is_sunk:
            # Clear targeting context and queued targets for this ship
            self._hits_by_ship.pop(ship_key, None)
            self._purge_queue_around(hits)
            return

        # Managed a hit but ship not sunk, so determine next guess.
        self._enqueue_targets(opponent, ship_key)

    def _enqueue_targets(self, opponent: BasePlayer, ship_key: str) -> None:
        """Insert next best targets based on current hits on a ship."""
        hits: list[CoordType] = sorted(self._hits_by_ship.get(ship_key, set()))
        if not hits:
            return

        if len(hits) == 1:
            self._enqueue_after_single_hit(opponent, hits[0])

        aligned = self._aligned_hits_or_none(hits)
        if aligned is None:
            self._enqueue_after_single_hit(opponent, hits[-1])
            return

        mode, cells = aligned
        self._enqueue_along_alignment(opponent, mode, cells)

    def _enqueue_after_single_hit(
            self, opponent: BasePlayer, hit: CoordLike
    ) -> None:
        """Hit one target so pick one of its four nearest neighbours."""
        self._enqueue_if_legal(
            opponent,
            cells=self._nearest_neighbours(Coordinate.from_xy(hit)))

    def _purge_queue_around(self, hits: set['CoordType']) -> None:
        """Remove queued cells that lie adjacent to a sunk ship.

        Keeps everything without bias.

        TODO:
         - Drop cells immediately adjacent to `hits` to bias elsewhere.
        """
        if not self._queued_moves or not hits:
            return

        self._queued_moves = list(self._queued_moves)

    @staticmethod
    def _aligned_hits_or_none(hits: list[CoordType]) -> Optional[tuple[ROW_COL_SYMBS, list[CoordType]]]:
        """Attempt to establish a vector between hits to pick along it.

        Two or more hits may define a line. If so, the next picked cell should
        be adjacent to either end of this line.
        """
        same_row: dict[int, list['CoordType']] = {}
        same_col: dict[int, list['CoordType']] = {}

        for x, y in hits:
            same_row.setdefault(x, []).append((x, y))
            same_col.setdefault(y, []).append((x, y))

        for x, cells in same_row.items():
            if len(cells) >= 2:
                cells.sort(key=lambda c: c[1])
                return 'row', cells

        for y, cells in same_col.items():
            if len(cells) >= 2:
                cells.sort(key=lambda c: c[0])
                return 'col', cells

        return None

    def _enqueue_along_alignment(
            self, opponent: BasePlayer, mode: ROW_COL_SYMBS, cells: list['CoordType']
    ) -> None:
        first, last = cells[0], cells[-1]
        if mode == 'row':
            x = first[0]
            y_left, y_right = first[1] - 1, last[1] + 1
            candidates = [(x, y_left), (x, y_right)]
        else:
            y = first[1]
            x_up, x_down = first[0] - 1, last[0] + 1
            candidates = [(x_up, y), (x_down, y)]

        self._enqueue_if_legal(opponent, candidates)
