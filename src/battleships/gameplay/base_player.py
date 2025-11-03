#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file base_player.py)

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
        src/battleships/base_player.py
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
from typing import Any, Optional, TYPE_CHECKING, Union

# Third-party imports
from pydantic import BaseModel, ConfigDict, Field

# Local application imports
from board_games import Coordinate
from battleships.board import Board
from battleships.ships import Fleet
import battleships.shots as shots

if TYPE_CHECKING:
    from battleships.shots import Info, Outcome

from utils import Divider, load_yaml
from src.log import get_logger

log = get_logger(__name__)

# Module-level constants
DEFAULT_PLAYER: str = 'battleships/config/player.yml'
"""Default relative path to a player's configuration file."""

__all__ = ['DEFAULT_PLAYER', 'BasePlayer']


class BasePlayer(BaseModel, ABC):
    """Common base player interface without any UI.

    Each player manages their own fleet, board and shot history.

    Attributes:
        name: Player's username.
        id: Index of this player within manager's list: ``Battleships.players``.
        fleet: All ships and their positions.
        board: 2D grid storing current game-state.
    """
    model_config = ConfigDict(validate_default=True)

    name: str
    id: int
    # Defaults initialised via static helpers to simplify class' init.
    fleet: Fleet = Field(default_factory=lambda: BasePlayer.default_fleet())
    board: Board = Field(default_factory=lambda: BasePlayer.default_board())
    guesses: list[Coordinate] = Field(default_factory=list)

    @staticmethod
    def default_fleet() -> 'Fleet':
        return Fleet.load_from_yaml(fleet_id='basic_fleet_1')

    @staticmethod
    def default_board() -> 'Board':
        return Board(height=10, width=10)

    def _banner(self) -> Optional[str]:
        """Console title announcing the player."""
        # TODO: Turn below f-string into easier-to-read print format
        banner = Divider.console.make_title("Player", self.name)
        print(f"\n{banner}")
        return banner

    @property
    def is_still_playing(self) -> bool:
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

    def place_fleet(self) -> None:
        """Place this player's fleet onto their board."""
        for ship in self.fleet.ships.values():
            if ship.placement is None:
                continue

            self.board.place(pos=ship.placement,
                             symbol=(ship.symbol or ship.spec.symbol))

    def record_shot(self, shot: Coordinate) -> None:
        """

        Arguments:
            shot:
        """
        self.guesses.append(shot)

    def take_turn(self, opponent: 'BasePlayer') -> 'Outcome':
        """Orchestrator for a single turn.

        Shared flow that delegates to optional overloaded methods for input.

        Method supports I/O.

        Arguments:
            opponent:

        TODO:
         - Fix warning of returned type 'Expected type 'Outcome',
           got 'Literal[Outcome.INVALID, Outcome.ERROR, Outcome.OUT] | None | Any'
           instead'.
        """
        while True:
            raw = self._get_shot_input(opponent)

            if _is_command(raw):
                # Subclass hasn't command semantics
                continue

            coord = Coordinate.coerce(raw)
            turn = shots.Engine.process(opponent.board, opponent.fleet,
                                        coord)

            if turn.outcome not in (shots.Outcome.INVALID,
                                    shots.Outcome.ERROR,
                                    shots.Outcome.OUT):
                self.record_shot(turn.coord)

            if turn.outcome in shots.Outcome.failures():
                self._on.outcome(turn, opponent, printable=False)
                continue

            self._on_outcome(turn, opponent, printable=False)
            return turn.outcome

    @abstractmethod
    def end_turn(self) -> None:
        """Orchestrator to end a player's turn."""

    def _get_shot_input(self, opponent: 'BasePlayer') -> Union[str, Any]:
        """A raw user input OR a Commands enum.

        Returns raw string so `shots.Engine` existing coerce path keeps working.
        """
        raise NotImplementedError

    def _on_outcome(
            self, info: 'Info', opponent: 'BasePlayer', *, printable: bool
    ) -> None:
        """Hook for subclasses to notify users about the shot's outcome."""
        return

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


def _is_command(x: Any) -> bool:
    """Placed here to decouple this module from 'gameplay/messages.py'."""
    try:
        from battleships.gameplay.messages import Commands
        return isinstance(x, Commands)
    except Exception:
        # TODO: Fix overly broad exception clause
        return False
