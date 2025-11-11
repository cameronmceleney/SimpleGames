"""(One liner introducing this file commands.py)

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
        src/battleships/commands.py
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
from enum import auto, Enum
from typing import Literal, overload, Protocol

# Third-party imports

# Local application imports
from board_games.commands import (
    CommandSpec,
    CommandRegistry,
    CommandParser,
    RegistryProto,
    typed_registry
)

# Module-level constants


class Command(Enum):
    """Commands for printing a string when a keyword is detected in I/O."""
    HELP = auto()
    EXIT = auto()
    PAUSE = auto()
    GUESS = auto()
    SHOW_OWN_FLEET = auto()
    SHOW_OPP_FLEET = auto()


# Concrete CommandSpecs
_HELP = CommandSpec(
    command=Command.HELP,
    labels=('help',),
    message="Enter co-ordinates like 'B,3' or '2 5.\nCommands: {commands}"
)

_EXIT = CommandSpec(
    command=Command.EXIT,
    labels=('exit', 'quit',),
    message="Exiting the game."
)

_PAUSE = CommandSpec(
    command=Command.PAUSE,
    labels=('pause',),
    message="Game paused. Press Enter to continue playing."
)

_MAKE_GUESS = CommandSpec(
    command=Command.GUESS,
    labels=('guess', 'shot'),
    message=">>> Enter the co-ordinates of your next shot: "
)

_SHOW_OWN = CommandSpec(
    command=Command.SHOW_OWN_FLEET,
    labels=('fleet', 'board', 'me'),
    message='Fleet view'
)

_SHOW_OPP = CommandSpec(
    command=Command.SHOW_OPP_FLEET,
    labels=('opponent', 'enemy', 'opp'),
    message='Targeting view'
)

SPECS: tuple[CommandSpec[Command], ...] = (
    _HELP, _EXIT, _PAUSE,  # Mandatory
    _MAKE_GUESS, _SHOW_OWN, _SHOW_OPP  # Battleships specific
)


class BattleshipsRegistryProto(RegistryProto[Command], Protocol):
    HELP: CommandSpec[Command]
    EXIT: CommandSpec[Command]
    PAUSE: CommandSpec[Command]
    GUESS: CommandSpec[Command]
    SHOW_OWN_FLEET: CommandSpec[Command]
    SHOW_OPP_FLEET: CommandSpec[Command]


class BattleshipsRegistry(CommandRegistry[Command]):
    @overload
    def __getattr__(
            self,
            name: Literal['HELP', 'EXIT', 'PAUSE', 'GUESS', 'SHOW_OWN_FLEET', 'SHOW_OPP_FLEET']
    ) -> CommandSpec[Command]: ...

    def __getattr__(self, name: str) -> CommandSpec[Command]:
        return super().__getattr__(name)


REGISTRY: BattleshipsRegistryProto = typed_registry(
    BattleshipsRegistryProto,
    CommandRegistry(Command, SPECS)
)
PARSER = CommandParser(REGISTRY)
is_command_token = PARSER.is_token


if __name__ == "__main__":

    print(REGISTRY.HELP)
