"""Utils file."""

# Standard library imports
from enum import StrEnum
from pathlib import Path
from textwrap import indent
from typing import Any, Literal, Optional

# Third-party imports
import yaml

# Local application imports


__all__ = [
    'AlignText',
    'JustifyText',
    'Divider',
    'CleanText',
    'load_yaml'
]


class AlignText(StrEnum):
    LEFT = '<'
    RIGHT = '>'
    CENTER = '='


class JustifyText:
    _default_width: int = 24  # class-wide default
    _align_map = AlignText

    @classmethod
    def _fmt(
        cls,
        s: Any,
        *,
        fill: str = ' ',
        align: Literal['left', 'center', 'right'] = 'left',
        width: int | None = None,
        end: str = '\n'
    ) -> str:
        """Justify and format text."""
        if len(fill) != 1:
            raise ValueError("Fill must be a single character")

        align_ = cls._align_map[align.upper()]
        width_ = cls._default_width if width is None else int(width)

        return f"{str(s):{fill}{align_}{width_}}{end}"

    @classmethod
    def value(
        cls,
        text: Any,
        *,
        align: Literal['left', 'center', 'right'] = 'left',
        width: Optional[int] = None,
        end: str = '\n'
    ) -> str:
        return cls._fmt(text, align=align, width=width, end=end)

    @classmethod
    def kv(
        cls,
        key: Any,
        value: Any,
        *,
        align: Literal['left', 'right'] = 'left',
        width: Optional[int] = None,
        sep: str = ' ',
        value_repr: bool = False,
        end: str = '\n'
    ) -> str:
        """Justify a key-value pair."""
        left = cls._fmt(key, align=align, width=width, end='')
        right = repr(value) if value_repr else value
        return f"{left}{sep}{right}{end}"

    @classmethod
    def col(
        cls,
        text: Any,
        *,
        align: Literal['left', 'right'] = 'left',
        width: Optional[int] = None,
        fill: str = ' ',
        end: str = ''
    ) -> str:
        """Generic column format."""
        return cls._fmt(text, align=align, width=width, fill=fill, end=end)

    @classmethod
    def cols(
        cls,
        *text: Any,
        sep: str = ' ',
        align: Literal['left', 'right'] = 'left',
        width: Optional[int] = None,
        fill: str = ' ',
        end: str = '\n'
    ) -> str:
        """Format multiple columns and join."""
        parts = [cls._fmt(t, align=align, width=width, fill=fill, end='') for t in text]
        return sep.join(parts) + end

    @classmethod
    def indent(
        cls,
        *lines: str,
        width: Optional[int] = None,
        levels: int = 1,
        fill: str = ' ',
    ) -> str:
        text = '\n'.join(lines)
        width_ = cls._default_width if width is None else int(width)
        prefix = fill * width_ * levels
        return indent(text, prefix)


class Divider(StrEnum):
    """Immutable collection of string dividers.

    Attributes:
        text: 8 chars long
        section: 16 chars long
        console: 32 chars long.
    """
    # NOTE: Preferred ``StrEnum`` over ``Dict`` for dot access and over
    # ``dataclass`` because no further initialisation is required.
    _char = '-'

    text = 8 * _char + '\n'
    section = 16 * _char + '\n'
    console = 32 * _char + '\n'

    def make_title(
        self,
        header: Any,
        details: Optional[Any] = None,
        *,
        wrap: bool = False,
        prefix: tuple[str, str] = ('<', '>'),
        suffix: tuple[str, str] = ('', ''),
        **kwargs
    ) -> str:
        title_ = JustifyText.kv(key=f"{prefix[0]}{str(header).capitalize()}{prefix[1]}",
                                value=f"{suffix[0]}{str(details).capitalize()}{suffix[1]}",
                                **kwargs)
        return '\n' + (self if wrap else '') + title_ + self


class CleanText:

    @staticmethod
    def truthy(truthy: bool) -> str:
        """Return yes/no instead of True/False from a boolean."""
        return 'Yes' if truthy else 'No'

    @staticmethod
    def ship_name(name: str, *, sep: str = '-', fill: str = ' ') -> str:
        """Turn 'my_ship_name' into 'My Ship Name'."""
        msg = [s.capitalize() for s in name.split(sep)]
        return fill.join(msg)

    @staticmethod
    def bf(c: Any) -> str:
        """Make a string boldface."""
        return f"\033[1m{str(c)}\033[0m"


def load_yaml(
        filename: str,
        *,
        safe_mode: bool = True,
) -> dict:
    filepath = Path(filename).resolve()
    loader = yaml.SafeLoader if safe_mode else yaml.FullLoader
    contents = yaml.load(filepath.read_text(), Loader=loader)
    return contents

# if __name__ == "__main__":
#     J = JustifyText
#
#     # Key–value lines
#     print(Divider.console)
#     print('KV')
#     print(J.kv("Ship", "Destroyer", end=''))
#     print(J.kv("Size", 2), end="")
#     print(J.kv("Cloaked", False, value_repr=False), end="")
#
#     # Generic column usage
#     print(Divider.console)
#     sname = J.col("aircraft_carrier")
#     size = J.col("5", align="left")
#     print(f"{sname}{size}")
#
#     # Indent a block
#     print('indent')
#     block = "line1\nline2\nline3"
#     print(J.indent(block, levels=1))
#
#     print(Divider.console.make_title('Aircraft Carrier', details='bye', width=23))
