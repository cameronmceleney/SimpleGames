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
        board_games/messages.py
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
from dataclasses import dataclass
from enum import StrEnum
from types import SimpleNamespace
from typing import cast, Protocol, Iterator

# Local application imports
from utils import Divider


class _MessageMemberLike(Protocol):
    """A single message field that can render itself."""
    def render(self, **kwargs) -> str: ...
    def __str__(self) -> str: ...


class _MessagesLike(Protocol):
    """Base container of message fields without helpers."""
    END_TURN_BLOCKING: _MessageMemberLike
    END_TURN: _MessageMemberLike
    WINNER: _MessageMemberLike
    KEEP_PLAYING: _MessageMemberLike
    ELIMINATED: _MessageMemberLike


class _PlayerMessagesLike(_MessagesLike, Protocol):
    """Base container of message fields with helpers.

    Used for player-facing messages.
    """
    @staticmethod
    def banner(name: str) -> str: ...
    def __iter__(self) -> Iterator[_MessageMemberLike]: ...
    def __call__(self, name: str) -> _MessagesLike: ...
    def __repr__(self) -> str: ...


class Messages(StrEnum):
    """Text that is displayed in the console."""
    END_TURN_BLOCKING = ">>> Press 'Enter' to end turn..."
    END_TURN = "Turn complete."
    WINNER = "Congratulations on winning!"
    KEEP_PLAYING = "No winner (no active players)."
    ELIMINATED = "You've been eliminated!"

    def render(self, **kwargs) -> str:
        """Render messages with optional placeholders."""
        return str(self).format(**kwargs)


@dataclass(frozen=True)
class _PrefixedMessage:
    """Wraps a message member to prefix it with '<Name>: ' when rendered."""
    member: _MessageMemberLike
    prefix: str

    def _display_name(self) -> str:
        """Capitalise the first letter of prefix."""
        return self.prefix.capitalize()

    def render(self, **kwargs) -> str:
        return f"{self._display_name()}: {self.member.render(**kwargs)}"

    def __str__(self) -> str:
        """Delegates to ``_PrefixedMessage.render()``."""
        return self.render()


@dataclass(frozen=True)
class _PlayerMessagesFacade(_PlayerMessagesLike):
    """Singleton facade that forwards attribute access to the private enum."""

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} 'PlayerMessages'>"

    def __getattr__(self, name: str) -> _MessageMemberLike:
        try:
            return getattr(Messages, name)
        except AttributeError as e:
            raise AttributeError(f"Unknown message '{name}'") from e

    def __iter__(self) -> Iterator[_MessageMemberLike]:
        for m in Messages:
            yield cast(_MessageMemberLike, m)

    def __call__(self, name: str) -> _MessagesLike:
        """Return a lightweight objet whose attributes mirror `Messages`.

        Enables chaining. """
        ns = SimpleNamespace()
        for key, member in Messages.__members__.items():
            setattr(ns, key, _PrefixedMessage(member=member, prefix=name))
        return cast(_MessagesLike, ns)

    @staticmethod
    def banner(name: str) -> str:
        return f"\n{Divider.console.make_title('Player', name)}"


PlayerMessages: _PlayerMessagesLike = _PlayerMessagesFacade()

# print(PlayerMessages('Alice').ELIMINATED)
# print(PlayerMessages.banner('Alice'))
