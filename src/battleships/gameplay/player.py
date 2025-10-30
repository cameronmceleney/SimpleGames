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
from typing import Optional, TYPE_CHECKING

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field

# Local application imports
from board_games import Coordinate
from battleships.board import Board, Symbols
from battleships.ships import Fleet
from battleships.shots import Engine as ShotsEngine

from .messages import PlayerMessages

from utils import Divider, load_yaml
from src.log import get_logger

if TYPE_CHECKING:
    from battleships.shots import Outcome as ShotsOutcome

log = get_logger(__name__)

# Module-level constants
DEFAULT_PLAYER: str = 'battleships/config/player.yml'
"""Default relative path to a player's configuration file."""

__all__ = ['DEFAULT_PLAYER', 'Player']


class Player(BaseModel):
    """Game player with their own fleet, board and shot history.

    Attributes:
        name: Player's username.
        id: Index of this player within manager's list: ``Battleships.players``.
        fleet: All ships and their positions.
        board: 2D grid storing current game-state.
        shots: All shots (guessed grid-tiles) by this player.
    """
    model_config = ConfigDict(validate_default=True)

    name: str
    id: int
    # Defaults initialised via static helpers to simplify class' init.
    fleet: Fleet = Field(default_factory=lambda: Player.default_fleet())
    board: Board = Field(default_factory=lambda: Player.default_board())

    shots: list[Coordinate] = Field(
        default_factory=list,
        validation_alias='shots'
    )

    @staticmethod
    def default_fleet(fleet_id: str = 'basic_fleet_1') -> 'Fleet':
        return Fleet.load_from_yaml(fleet_id=fleet_id)

    @staticmethod
    def default_board(height: int = 10, width: int = 10) -> 'Board':
        return Board(height=height, width=width)

    @property
    def is_playing(self) -> bool:
        """Check if this player has any surviving ships."""
        return self.fleet.is_alive

    def apply_positions(self, filepath: Optional[str]) -> None:
        """Load and place onto their board a player's ship placements.

        Arguments:
            filepath: Relative path to file containing ship placements.
        """
        # TODO. Add error check for filepath
        player_data = load_yaml(filepath if filepath else {})
        log.debug(player_data)

        self.fleet.apply_placements(player_data)
        self.place_fleet()

    def place_fleet(self, *, symbol_strategy: str = 'initial') -> None:
        """Place this player's fleet onto their board."""
        for ship in self.fleet.ships.values():
            if ship.placement is None:
                continue

            self.board.place(ship.placement, symbol=(ship.symbol or ship.spec.symbol))

    @staticmethod
    def apply_shot(target_player: 'Player', shot: Coordinate) -> 'ShotsOutcome':
        """Core logic for a player taking a shot.

        Method doesn't support I/O. For the rules applied to each `shot` see
        the attribute descriptions of ``ShotsOutcome``.

        Arguments:
            target_player: Another player's (game-specific) board being aimed at.
            shot: Grid-tile attempting to be shot.
        """
        board = target_player.board
        if not board.in_bounds(shot):
            return ShotsOutcome.OUT

        cell = board.get(shot)
        if cell in (Symbols.HIT, Symbols.MISS):
            return ShotsOutcome.REPEAT

        # Check opponent's fleet for hit tracking
        outcome, ship = target_player.fleet.register_shot(shot)
        if outcome is ShotsOutcome.MISS:
            board.mark_miss(shot)
        elif outcome is ShotsOutcome.HIT:
            board.mark_hit(shot)
            # TODO. Add ability to mark sunk ships differently.
        else:
            # Guarding against a missed ShotsOutcome.REPEAT
            pass

        return outcome

    def record_shot(self, shot: Coordinate) -> None:
        self.shots.append(shot)

    def take_turn(self, opponent: 'Player') -> 'ShotsOutcome':
        """Orchestrator for a single turn.

        Method supports I/O.

        Steps:
            1. Prompt player for a shot.
            2. Coerce and apply it to the opponent's board.
            3. Print the outcome of the shot.
            4. Record valid shots

        Arguments:
            opponent: Another player to target.
        """
        raw = input(f"<Player {self.name}> {PlayerMessages.make_guess}")

        info = ShotsEngine.process(opponent.board, opponent.fleet, raw)
        if info.outcome not in (ShotsOutcome.INVALID, ShotsOutcome.ERROR, ShotsOutcome.OUT):
            self.record_shot(info.coord)

        print(f"<Player {self.id}> {info.outcome.message}")

        return info.outcome

    @staticmethod
    def end_turn() -> None:
        """Orchestrator to end a player's turn."""
        print('\n' * 2)

    def __repr__(self, print_headers: bool = True) -> str:
        """Display all the key attributes of the player."""

        msg = Divider.console if print_headers else ''

        msg += Divider.console.make_title('Player', {self.name})

        msg += repr(self.fleet)
        msg += Divider.console
        msg += repr(self.board)
        msg += Divider.console

        return msg

    def __str__(self) -> str:
        return f"<Player {self.id}> {self.name} | shots={len(self._shots)}"
