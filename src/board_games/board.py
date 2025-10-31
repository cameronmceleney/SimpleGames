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
from typing import Any, Callable, Literal

# Third-party imports
from pydantic.dataclasses import dataclass

# Local application imports
from .coordinate import Coordinate
from .grid import Grid


@dataclass(slots=True)
class Board(Grid):
    """2D game board with bounds-checked cell access and rendering.

    This class contains methods general to all 2D board games.

    Attributes:
        height:
        width:
        grid:
        symbols:
    """
    ...

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

    def render(
        self,
        show_guides: bool = True,
        *,
        row_symbols: Literal['let', 'num'] = 'let',
        col_symbols: Literal['let', 'num'] = 'num'
    ) -> str:
        """Render a string view of the current board-state."""
        lines: list[str] = []
        start_char = 65  # chr(65) = 'A'
        pad: str = self.symbols.EMPTY * (4 if show_guides else 2)

        sym = self.symbols  # Alias to shorten code of print statements

        match col_symbols:
            case 'let':
                cid_iters = (chr(start_char + j) for j in range(self.width))
            case 'num':
                cid_iters = (str(j) for j in range(self.width))
            case _:
                raise ValueError(f"Invalid col_symbols.")

        col_ids = sym.EMPTY.join(cid_iters)

        # Begin rendering Board
        if show_guides:
            lines.append(pad + col_ids)

        # Generate each row of the grid with its identifier
        for i in range(self.height):
            row = self.grid[i]
            if show_guides:
                # Add row label to grid starting from 'A'
                match row_symbols:
                    case 'let': rid = chr(start_char + i)
                    case 'num': rid = i
                    case _: raise ValueError(f"Invalid row_symbol)")

                lines.append(f"{rid}{sym.SPACE}"
                             f"{sym.HORIZONTAL_DIVIDER}{sym.SPACE}"
                             f"{sym.EMPTY.join(row)}")
            else:
                lines.append(self.symbols.EMPTY.join(row))

        if show_guides:
            hline = self.width * (sym.VERTICAL_DIVIDER + sym.SPACE)
            lines.insert(1, pad + hline)

        return '\n'.join(lines) + '\n'

    def render_with_mask(
            self,
            mask: Callable,
            show_guides: bool = True,
            *,
            row_symbols: Literal['let', 'num'] = 'let',
            col_symbols: Literal['let', 'num'] = 'num'
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
        lines: list[str] = []
        start_char = 65
        pad: str = self.symbols.EMPTY * (4 if show_guides else 2)

        match col_symbols:
            case 'let':
                cid_iters = (chr(start_char + j) for j in range(self.width))
            case 'num':
                cid_iters = (str(j) for j in range(self.width))
            case _:
                raise ValueError(f"Invalid col_symbols.")

        col_ids = self.symbols.EMPTY.join(cid_iters)

        if show_guides:
            lines.append(pad + col_ids)
            hline = self.width * (self.symbols.VERTICAL_DIVIDER + self.symbols.EMPTY)
            lines.append(pad + hline)

        for i in range(self.height):
            row = [mask(ch) for ch in self.grid[i]]
            if show_guides:
                rid = chr(start_char + i) if row_symbols == 'let' else i
                lines.append(f"{rid}"
                             f"{self.symbols.SPACE}"
                             f"{self.symbols.HORIZONTAL_DIVIDER}"
                             f"{self.symbols.SPACE}"
                             f"{self.symbols.EMPTY.join(row)}")
            else:
                lines.append(self.symbols.EMPTY.join(row))

        return '\n'.join(lines) + '\n'


