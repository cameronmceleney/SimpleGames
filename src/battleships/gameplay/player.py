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
from pydantic import AliasChoices, BaseModel, ConfigDict, Field

# Local application imports
from board_games import Coordinate
from battleships.board import Board
from battleships.ships import Fleet
import battleships.shots as shots

from .messages import parse, Commands, Registry, make_guess_cmd, exit_cmd, help_cmd, show_opp_cmd, show_own_cmd

if TYPE_CHECKING:
    from battleships.shots import Outcome


from utils import Divider, load_yaml
from src.log import get_logger

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
        guesses: All shots guessed by this player.
    """
    model_config = ConfigDict(validate_default=True)

    name: str
    id: int
    # Defaults initialised via static helpers to simplify class' init.
    fleet: Fleet = Field(default_factory=lambda: Player.default_fleet())
    board: Board = Field(default_factory=lambda: Player.default_board())

    guesses: list[Coordinate] = Field(
        default_factory=list,
        validation_alias=AliasChoices('guesses', 'shots')
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

    def record_shot(self, shot: Coordinate) -> None:
        self.guesses.append(shot)

    def take_turn(self, opponent: 'Player') -> 'Outcome':
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
        print(f"\n{Divider.console.make_title(f"Player", f"{self.name}")}")
        opponent.board.show(mode='opponent')

        # Prompt for next shot
        while True:
            raw = input(make_guess_cmd)
            cmd = parse(raw)

            if cmd is Commands.EXIT:
                print(exit_cmd())
                raise SystemExit
            elif cmd is Commands.HELP:
                print(help_cmd(commands=Registry.instance().commands_list()))
            elif cmd is Commands.SHOW_OWN_FLEET:
                print(show_own_cmd())
                self.board.show(mode="self", show_guides=True)
            elif cmd is Commands.SHOW_OPP_FLEET:
                print(show_opp_cmd())
                opponent.board.show(mode="opponent", show_guides=True)

            # No special commands; process shot
            shot_attempt = shots.Engine.process(opponent.board, opponent.fleet, raw)
            print(shot_attempt.outcome.message)

            if shot_attempt.outcome not in (shots.Outcome.INVALID, shots.Outcome.ERROR, shots.Outcome.OUT):
                self.record_shot(shot_attempt.coord)

            if shot_attempt.outcome in shots.Outcome.failures():
                continue

            return shot_attempt.outcome

    @staticmethod
    def end_turn() -> None:
        """Orchestrator to end a player's turn."""
        input("Press Enter to end turn...")
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
        return f"<Player {self.id}> {self.name} | guesses={len(self.guesses)}"
