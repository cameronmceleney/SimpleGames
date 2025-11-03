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
from random import randrange, choice
from typing import Union

# Third-party imports

# Local application imports
from board_games.coordinate import coordinate_type
import battleships.shots as shots


from .messages import (
    parse,
    Commands,
    Registry,
    make_guess_cmd, exit_cmd, help_cmd, show_opp_cmd, show_own_cmd)

from .base_player import BasePlayer, DEFAULT_PLAYER
from .messages import Message
from src.log import get_logger

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
            self, info: 'shots.Info', opponent: 'HumanPlayer', *, printable: bool
    ) -> None:
        print(info.outcome.message)

    def end_turn(self) -> None:
        input(Message.END_TURN)
        print('\n' * 2)


class AIPlayer(BasePlayer):
    """Computer-controlled player object.

    Uses random selection to make guesses.

    Attributes:
        _tried: Lightweight set of previous coordinates (in tuple form)

    TODO:
     - Add logic so that the AI places their own ships.
    """
    _tried: set[tuple[int, int]] = set()

    def _get_shot_input(self, opponent: 'BasePlayer') -> Union[str, object]:
        self._tried.add(self.generate_shot(opponent))

    def generate_shot(self, opponent: 'BasePlayer') -> coordinate_type:
        """Generate a random shot.

        Generates shot by building candidate list of untried cells on the
        opponent's board.

        Returns:
            ``(x,y)``
        """
        # Tried using longer list-comprehension instead of nested for loops
        candidates = [(x, y)
                      for x in range(opponent.board.height)
                      for y in range(opponent.board.width)
                      if (x, y) not in self._tried]

        # Tried using longer tertiary operator to remove if/else block
        if candidates:
            return choice(candidates)
        else:
            return randrange(opponent.board.height), opponent.board.width

    def end_turn(self) -> None:
        input(Message.AI_END_TURN)
        print('\n' * 2)
