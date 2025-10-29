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
from enum import StrEnum
from pydantic import BaseModel, ConfigDict, Field
from typing import Any, Optional

from battleships.domain.shot_info import ShotOutcome
# Third-party imports

# Local application imports
from src.battleships.domain.fleet import Fleet
from src.battleships.domain.board import BattleshipBoard, Symbols
from src.utils.utils import Divider, load_yaml
from src.battleships.domain.coordinate import Coordinate
from src.battleships.domain.shot_info import ShotEngine


# Module-level constants
PLAYER_FILE_PATH = "config/player.yml"

from src.log import get_logger

log = get_logger(__name__)

__all__ = ['Player', 'MESSAGES']

MESSAGES: dict = {
    'make_guess': "Enter the co-ordinates of your next shot: "
}
"""Messages to display to the player."""


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
    board: BattleshipBoard = Field(default_factory=lambda: Player.default_board())

    shots: list[Coordinate] = Field(
        default_factory=list,
        validation_alias='shots'
    )

    @staticmethod
    def default_fleet(fleet_id: str = 'basic_fleet_1') -> Fleet:
        return Fleet.load_from_yaml(fleet_id=fleet_id)

    @staticmethod
    def default_board(height: int = 10, width: int = 10) -> BattleshipBoard:
        return BattleshipBoard(height=height, width=width)

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

            self.board.place(ship.placement, symbol=ship.symbol)

    @staticmethod
    def apply_shot(target_player: 'Player', shot: Coordinate) -> 'ShotOutcome':
        """Core logic for a player taking a shot.

        Method doesn't support I/O. For the rules applied to each `shot` see
        the attribute descriptions of ``ShotOutcome``.

        Arguments:
            target: Another player's (game-specific) board being aimed at.
            shot: Grid-tile attempting to be shot.
        """
        board = target_player.board
        if not board.in_bounds(shot):
            return ShotOutcome.OUT

        cell = board.get(shot)
        if cell in (Symbols.HIT, Symbols.MISS):
            return ShotOutcome.REPEAT

        # Check opponent's fleet for hit tracking
        outcome, ship = target_player.fleet.register_shot(shot)
        if outcome is ShotOutcome.MISS:
            board.mark_miss(shot)
        elif outcome is ShotOutcome.HIT:
            board.mark_hit(shot)
            # TODO. Add ability to mark sunk ships differently.
        else:
            # Guarding against a missed ShotOutcome.REPEAT
            pass

        return outcome

    def record_shot(self, shot: Coordinate) -> None:
        self.shots.append(shot)

    def take_turn(self, opponent: 'Player') -> 'ShotOutcome':
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
        raw = input(f"<Player {self.name}> {MESSAGES['make_guess']}")

        info = ShotEngine.process(opponent.board, opponent.fleet, raw)
        if info.outcome not in (ShotOutcome.INVALID, ShotOutcome.ERROR, ShotOutcome.OUT):
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
