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
from enum import Enum
from dataclasses import dataclass
from typing import (
    Any,
    Callable,
    cast,
    Generic,
    Iterable,
    Literal,
    Mapping,
    Optional,
    Protocol,
    overload,
    Sequence,
    Type,
    TypeGuard,
    TypeVar
)

# Third-party imports

# Local application imports

# Module-level constants
C = TypeVar('C', bound=Enum)
"""Bound to downstream ``Command(Enum)`` implementations."""


class _SafeFormatDict(dict):
    def __missing__(self, key: str) -> str:
        return '{' + key + '}'


@dataclass(frozen=True)
class CommandSpec(Generic[C]):
    """Description of a command token.

    Attributes:
        command: The enum member for this command.
        labels: Primary label, then aliases (case insensitive).
        message: Optional help text.
        parse: Optional payload parser
    """
    command: C
    labels: Sequence[str]
    message: str = ''
    parse: Optional[Callable[[str], Any]] = None

    def __post_init__(self):
        if not self.labels:
            raise ValueError("CommandSpec.labels must not be empty.")

        normalised_labels = ((self.labels,) if isinstance(self.labels, str) else tuple(self.labels,))
        object.__setattr__(self, 'labels', tuple(normalised_labels))

    @property
    def name(self) -> str:
        return self.labels[0]

    @property
    def aliases(self) -> Sequence[str]:
        return self.labels[1:]

    @property
    def label_join(self) -> str:
        return '/'.join(self.labels)

    def render(self, **fmt) -> str:
        if not self.message:
            return ''
        return self.message.format_map(_SafeFormatDict(fmt))

    def matches(self, token: str) -> bool:
        """Check if `token` matches any `label` for this command."""
        t = token.strip().lower()
        return any(t == lb.lower() for lb in self.labels)

    def __str__(self) -> str:
        return self.render()

    def __call__(self, **fmt: Any) -> str:
        return self.render(**fmt)


class RegistryProto(Protocol[C]):
    HELP: CommandSpec[C]
    EXIT: CommandSpec[C]
    PAUSE: CommandSpec[C]


class CommandRegistry(Generic[C], Mapping[str, CommandSpec[C]]):
    """Provides token and enum lookups with attribute and mapping access.

    Attributes:
        _by_enum:
        _by_token:
    """
    _by_enum: dict[C, CommandSpec[C]]
    _by_token: dict[C, CommandSpec[C]]
    _by_name: dict[str, CommandSpec[C]]
    _token_type: type[C]

    def __init__(
            self, token_type: type[C], specs: Iterable[CommandSpec[C]], *,
            required: Iterable[str] | None = ('HELP', 'EXIT', 'PAUSE')
    ) -> None:
        """
        Arguments:
             specs:
        """
        self._token_type = token_type
        self._by_enum = {s.command: s for s in specs}
        self._by_token: dict[str, CommandSpec] = {
            tok.lower(): s
            for s in specs
            for tok in s.labels
        }
        self._by_name = {cmd.name.lower(): s for cmd, s in self._by_enum.items()}

        if not self._by_enum:
            raise ValueError("CommandRegistry requires at least one CommandSpec.")

        for cmd, spec in self._by_enum.items():
            object.__setattr__(self, cmd.name, spec)

        if required:
            missing = [n for n in required if not hasattr(self, n)]
            if missing:
                raise ValueError(f"Registry missing required commands: {', '.join(missing)}")

    def __getitem__(self, key: str) -> CommandSpec[C]:
        # Allow lookup by canonical name or primary label
        k = key.lower()
        # enum-name path
        if k in self._by_name:
            return self._by_name[k]

        if k in self._by_token:
            return self._by_token[k]

        raise KeyError(key)

    def __iter__(self) -> Iterable:
        return iter(self._by_name.keys())

    def __len__(self) -> int:
        return len(self._by_enum)

    @overload
    def __getattr__(self, name: Literal['HELP']) -> CommandSpec[C]: ...
    @overload
    def __getattr__(self, name: Literal['EXIT']) -> CommandSpec[C]: ...
    @overload
    def __getattr__(self, name: Literal['PAUSE']) -> CommandSpec[C]: ...
    @overload
    def __getattr__(self, name: str) -> CommandSpec[C]: ...

    def __getattr__(self, name: str) -> CommandSpec[C]:
        # Allow attribute access such as `registry.EXIT`.
        try:
            cmd = self._token_type[name]
        except KeyError as e:
            raise AttributeError(name) from e
        return self._by_enum[cmd]

    def find(self, token: str) -> Optional[CommandSpec[C]]:
        return self._by_token.get(token.strip().lower())

    def commands_list(self) -> str:
        return '; '.join(s.label_join for s in self._by_enum.values())

    @property
    def token_type(self) -> type[C]:
        return self._token_type


R = TypeVar('R')


def typed_registry(_: Type[R], reg: CommandRegistry[C]) -> R:
    return cast(R, reg)


def require_commands(reg: CommandRegistry[C], *required: str) -> None:
    """Runtime guard to ensure mandatory commands are present."""
    missing = [name for name in required if not hasattr(reg, name)]
    if missing:
        raise ValueError(f"Registry missing required commands: {', '.join(missing)}")


@dataclass(frozen=True)
class _Parsed(Generic[C]):
    """

    Attributes:
        spec:
        payload: Original input if not a command, else canonical token
    """
    spec: Optional[CommandSpec[C]]
    payload: str = ''
    value: Any = None

    @property
    def command(self) -> Optional[C]:
        return self.spec.command if self.spec else None


class CommandParser(Generic[C]):
    def __init__(self, registry: CommandRegistry[C]) -> None:
        self._r = registry
        self.is_token: Callable[[object], TypeGuard[C]] = make_token_checker(registry._token_type)

    def parse_info(self, raw: str) -> _Parsed[C]:
        token = raw.strip().lower()
        spec = self._r.find(token)

        if spec is None:
            return _Parsed(spec=None, payload=raw, value=None)

        value = spec.parse(raw) if spec.parse else spec.name
        return _Parsed(spec=spec, payload=spec.name, value=value)

    def parse(self, raw: str) -> Optional[C]:
        return self.parse_info(raw).command


def make_token_checker(token_type: type[C]) -> Callable[[object], TypeGuard[C]]:
    """Factory that results a TypeGuard checker for an enum type."""
    def _check(x: object) -> TypeGuard[C]:
        return isinstance(x, token_type)
    return _check
