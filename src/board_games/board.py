#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file board.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of board.py). Note that leading symbol '>>>' includes the 
    code in doctests, while '$' does not.)::
        
        >>> bar = 1
        >>> foo = bar + 1

(
Trailing paragraphs summarising final details.
)

Todo:
    * (Optional section for module-wide tasks).
    * (Use format: 'YYMMDD/task_identifier - one-liner task description'
    
References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/board/board.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        30 Oct 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from dataclasses import dataclass, field
from typing import (
    Any,
    Callable,
    ClassVar,
    Iterable,
    Literal,
    Optional,
    Self,
    Type,
    TypeAlias)

# Third-party imports
import numpy as np

# Local application imports
from .coordinate import Coordinate
from .symbols import SymbolsProto, DefaultSymbols

__all__ = ['BaseGrid', 'BaseBoard']

COL_AND_ROW_RENDER_SYMBOLS: TypeAlias = Literal['let', 'num']


@dataclass(slots=True)
class BaseGrid:
    """2D grid of mutable characters.

    Game-agnostic.

    Attributes:
        height:
        width:
        grid:
        symbols:
    """
    height: int
    width: int
    grid: np.ndarray = field(init=False, repr=False)

    symbols: ClassVar[Type[SymbolsProto]] = DefaultSymbols

    def __post_init__(self):
        self.grid = self._new_grid()

    def _new_grid(self) -> np.ndarray:

        """Allocate a new grid."""
        return np.full(shape=(self.height, self.width),
                       fill_value=self.symbols.EMPTY,
                       dtype='U1')  # 1-character unicode cells

    def reset(self, inplace: bool = True) -> Optional[np.ndarray]:
        """Reset the board to EMPTY."""
        new_grid = self._new_grid()

        if inplace:
            self.grid = new_grid
            return None

        return new_grid

    def clone(self) -> Self:
        """Deep copy the board including the grid."""
        g = type(self.__class__)(height=self.height, width=self.width)
        g.grid = self.grid.copy()
        return g


@dataclass(slots=True)
class BaseBoard(BaseGrid):
    """2D game board with bounds-checked cell access and rendering.

    This class contains methods general to all 2D board games.

    Attributes:
        height:
        width:
        grid:
        symbols:
    """

    def in_bounds(self, coord_like: Any) -> bool:
        """Check if a coordinate is within the grid."""
        coord = Coordinate.coerce(coord_like)
        return (0 <= coord.x < self.height) and (0 <= coord.y < self.width)

    def require_in_bounds(self, c: Any) -> None:
        coord = Coordinate.coerce(c)
        if not self.in_bounds(coord):
            raise IndexError(f"Coordinate is out of bounds: {coord.as_tuple()} "
                             f"<Board(height={self.height}, "
                             f"width={self.width})>")

    def get(self, coord_like: Any) -> str:
        """Read a cell.

        Return a Python scalar, not NumPy!
        """
        coord = Coordinate.coerce(coord_like)
        self.require_in_bounds(coord.as_tuple())
        return self.grid.item(coord.as_tuple())

    def set(self, coord_like: Any, symbol: str) -> None:
        """Write to a cell."""
        coord = Coordinate.coerce(coord_like)
        self.require_in_bounds(coord)

        if not (isinstance(symbol, str) and len(symbol) == 1):
            raise ValueError(f"Symbol must be single character, got: {symbol!r}")

        self.grid[coord.as_tuple()] = symbol

    def _col_ids(self, *,
                 col_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
                 start_char: int):
        match col_symbols:
            case 'let':
                cids = (chr(start_char + j) for j in range(self.width))
            case 'num':
                cids = (str(j) for j in range(self.width))
            case _:
                raise ValueError(f"Invalid col_symbols.")

        return self.symbols.EMPTY.join(cids)

    @staticmethod
    def _row_label(
            i: int, *,
            row_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
            start_char: int):
        return chr(start_char + i) if row_symbols == 'let' else str(i)

    def _render_core(
            self, *,
            show_guides: bool,
            row_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
            col_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
            row_map: Optional[Callable[[Iterable[str]], Iterable[str]]] = None
    ) -> str:
        """Common renderer."""

        lines: list[str] = []
        start_char = 65  # 'A'
        pad = self.symbols.EMPTY * (4 if show_guides else 2)

        # Header
        if show_guides:
            col_ids = self._col_ids(col_symbols=col_symbols,
                                    start_char=start_char)
            lines.append(pad + col_ids)
            hline = self.width * (self.symbols.VERTICAL_DIVIDER + self.symbols.SPACE)
            lines.append(pad + hline)

        # Body
        for i in range(self.height):
            row = self.grid[i]
            row_iter = row if row_map is None else row_map(row)

            joined = self.symbols.EMPTY.join(row_iter)

            if show_guides:
                rid = self._row_label(i, row_symbols=row_symbols,
                                      start_char=start_char)
                lines.append(f"{rid}{self.symbols.SPACE}"
                             f"{self.symbols.HORIZONTAL_DIVIDER}"
                             f"{self.symbols.SPACE}{joined}")
            else:
                lines.append(joined)

        return '\n'.join(lines)

    def render(
        self,
        show_guides: bool = True,
        *,
        row_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
        col_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'num'
    ) -> str:
        """Render a string view of the current board-state."""
        return self._render_core(
            show_guides=show_guides,
            row_symbols=row_symbols,
            col_symbols=col_symbols,
            row_map=None
        )

    def render_with_mask(
            self,
            mask: Callable[[str], str],
            show_guides: bool = True,
            *,
            row_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'let',
            col_symbols: COL_AND_ROW_RENDER_SYMBOLS = 'num'
    ):
        """Render board after transforming cells by applying a `mask`.

        Use cases include:
            - Displaying a player's guessed tiles (with hits and misses) during
              a game of Battleships.

        Arguments:
             mask:
             show_guides:
             row_symbols:
             col_symbols:

        TODO:
            - Simply `render_with_mask` and `render` by creating common private
              method.
        """
        def _apply(row: Iterable[str]) -> Iterable[str]:
            return (mask(ch) for ch in row)

        return self._render_core(
            show_guides=show_guides,
            row_symbols=row_symbols,
            col_symbols=col_symbols,
            row_map=_apply
        )

