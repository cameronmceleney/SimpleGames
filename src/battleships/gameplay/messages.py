#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file messages.py)

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
from enum import auto, Enum, StrEnum
from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Self

# Third-party imports

# Local application imports

# Module-level constants


class Message(StrEnum):
    """Text that is displayed in the console.

    TODO:
        - Find a way to distinguish 'Message' cases from 'Command' cases.
        - Turn `ELIMINATED` into method that prints actual player's name.
    """
    END_TURN = ">>> Press 'Enter' to end turn..."
    AI_END_TURN = "Turn complete."
    WINNER = 'Congratulations on winning!'
    KEEP_PLAYING = ' No winner (no active players).'
    ELIMINATED = "This player has been eliminated!"


class Command(Enum):
    """Commands for printing a string when a keyword is detected in I/O..

    TODO:
        - Find a way to distinguish 'Command' cases from 'Message' cases.
    """
    HELP = auto()
    EXIT = auto()
    GUESS = auto()
    SHOW_OWN_FLEET = auto()
    SHOW_OPP_FLEET = auto()


Commands = Command
"""Alias. """


def _is_command_token(x: Any) -> bool:
    """
    TODO:
     - Improve exception handling
     - Decide if this function should be bound to a class
    """
    try:
        return isinstance(x, COMMANDS)
    except Exception:
        return False


@dataclass(frozen=True)
class CommandSpec:
    command: Command
    labels: tuple[str, ...] | str
    message: str | None = None

    @property
    def _labels(self) -> tuple[str, ...]:
        return (self.labels,) if isinstance(self.labels, str) else self.labels

    @property
    def name(self) -> str:
        return self._labels[0]

    @property
    def aliases(self) -> tuple[str, ...]:
        return self._labels[1:]

    @property
    def label_join(self) -> str:
        return '/'.join(self.labels)

    def text(self, **fmt) -> str:
        if not self.message:
            return ''
        return self.message.format(**fmt)

    def show(self, **fmt) -> None:
        text = self.text(**fmt)
        if text:
            print(text)

    def __str__(self) -> str:
        return self.text()

    def __call__(self, **fmt) -> str:
        return self.text(**fmt)

    def matches(self, token: str) -> bool:
        t = token.strip().lower()
        return any(t == label.lower() for label in self._labels)


make_guess_cmd = CommandSpec(
    command=Command.GUESS,
    labels=('guess', 'shot'),
    message=">>> Enter the co-ordinates of your next shot: "
)

help_cmd = CommandSpec(
    command=Command.HELP,
    labels=('help',),
    message="Enter co-ordinates like 'B,3' or '2 5.\nCommands: {commands}"
)

exit_cmd = CommandSpec(
    command=Command.EXIT,
    labels=('exit', 'quit',),
    message="Exiting the game."
)

show_own_cmd = CommandSpec(
    command=Command.SHOW_OWN_FLEET,
    labels=('fleet', 'board', 'me'),
    message='Fleet view'
)

show_opp_cmd = CommandSpec(
    command=Command.SHOW_OPP_FLEET,
    labels=('opponent', 'enemy', 'opp'),
    message='Targeting view'
)

COMMANDS: tuple[CommandSpec, ...] = make_guess_cmd, help_cmd, exit_cmd, show_opp_cmd, show_own_cmd


class Registry:
    _inst: ClassVar[Optional['Registry']] = None

    def __init__(self) -> None:
        self._registry: dict[str, CommandSpec] = {
            'make_guess': make_guess_cmd,
            'help': help_cmd,
            'exit_cmd': exit_cmd,
            'show_opp_cmd': show_opp_cmd,
            'show_own_cmd': show_own_cmd,
        }

        self._tokens: dict[str, CommandSpec] = {}
        for spec in COMMANDS:
            for tok in spec._labels:
                self._tokens[tok.lower()] = spec

    @classmethod
    def instance(cls) -> Self:
        if cls._inst is None:
            cls._inst = cls()
        return cls._inst

    @property
    def registry(self) -> dict[str, CommandSpec]:
        return self._registry

    @property
    def tokens(self) -> dict[str, CommandSpec]:
        return self._tokens

    @staticmethod
    def commands_list() -> str:
        return '; '.join(spec.label_join for spec in COMMANDS)


@dataclass(frozen=True)
class Parsed:
    spec: Optional[CommandSpec]
    payload: str = ""  # original input if not a command, else canonical token

    @property
    def command(self) -> Optional[Command]:
        return self.spec.command if self.spec else None


def parse_info(raw: str) -> Parsed:
    """Rich parser."""
    tok = raw.strip()
    spec = Registry.instance().tokens.get(tok.lower())
    if spec is None:
        return Parsed(spec=None, payload=raw)
    return Parsed(spec=spec, payload=spec.name)


def parse(raw: str) -> Optional[Command]:
    """Lightweight parser."""
    p = parse_info(raw)
    return p.command


class PlayerMessages:
    @staticmethod
    def banner(name: str) -> None:
        from utils import Divider
        print(f"\n{Divider.console.make_title('Player', name)}")