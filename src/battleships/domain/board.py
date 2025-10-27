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
        src/battleships/domain/board.py
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
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, ClassVar, Literal, Optional, Type

# Third-party imports
import numpy as np


# Local application imports
from src.battleships.settings import BoardSettings
from src.utils.utils import CleanText, Divider, JustifyText
from src.battleships.domain.coordinate import Coordinate
from src.battleships.domain.position import Position


__all__ = [
    'Symbols',
    'Grid',
    'Board',
    'BattleshipBoard'
]


class Symbols(StrEnum):
    """Symbols to denote ships and actions on the playing board.

    Attributes:
        EMPTY: Alias ``space``.
        HIT
        MISS
        VERTICAL_DIVIDER: Alias ``vd``.
        HORIZONTAL_DIVIDER: Alias ``hd``.
    """
    EMPTY = ' '
    HIT = '#'
    MISS = '/'
    VERTICAL_DIVIDER = '–'
    HORIZONTAL_DIVIDER = '|'

    # Aliases
    space = EMPTY
    vd = VERTICAL_DIVIDER
    hd = HORIZONTAL_DIVIDER


@dataclass(slots=True)
class Grid:
    """2D grid of mutable characters.

    Attributes:
        height:
        width:
        grid:
        symbols:
    """
    height: int
    width: int
    grid: np.ndarray = field(init=False, repr=False)

    symbols: ClassVar[Type[Symbols]] = Symbols

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

    def clone(self) -> 'Grid':
        """Deep copy the board including the grid."""
        g = Grid(self.height, self.width)
        g.grid = self.grid.copy()
        return g


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
        x, y = coord.as_tuple()
        return (0 <= x < self.height) and (0 <= y < self.width)

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

        # Set column symbols and padding
        pad: str = self.symbols.EMPTY * (4 if show_guides else 2)

        match col_symbols:
            case 'let':
                cid_iters = (chr(start_char + j) for j in range(self.width))
            case 'num':
                cid_iters = (str(j) for j in range(self.width))
            case _:
                raise ValueError(f"Invalid col_symbols.")

        col_ids = self.symbols.EMPTY.join(cid_iters)

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

                lines.append(f"{rid}{self.symbols.space}"
                             f"{self.symbols.hd}{self.symbols.EMPTY}"
                             f"{self.symbols.EMPTY.join(row)}")
            else:
                lines.append(self.symbols.EMPTY.join(row))

        if show_guides:
            hline = (self.symbols.vd + self.symbols.EMPTY) * self.width
            lines.insert(1, pad + hline)

        return '\n'.join(lines) + '\n'


@dataclass(slots=True)
class BattleshipBoard(Board):
    """2D battleship game board as a grid of mutable characters.

    This class contains high-level helpers specific to Battleships games.

    Attributes:
        height:
        width:
        grid:
        symbols:
    """

    def mark_hit(self, c: Any) -> None:
        self.set(c, self.symbols.HIT)

    def mark_miss(self, c: Any) -> None:
        self.set(c, self.symbols.MISS)

    def place(self, pos: Any, symbol: str = 'S') -> None:
        """Place a multi-cell object onto the board.

        To place a ship do ``obj.place(ship.position, ship.symbol)``.
        """
        p = Position.coerce(pos)

        for coord in p.positions:
            self.set(coord, symbol)

    def show(self, *, show_guides: bool = True) -> None:
        print(self.render(show_guides=show_guides,
                          row_symbols='let', col_symbols='num'))

    def __repr__(self, print_headers: bool = True):

        msg = Divider.console if print_headers else ""
        msg += Divider.console.make_title('Board')

        for key, val in self.__dict__.items():
            if key == 'grid' or key[0] == '_':
                continue
            msg += JustifyText.kv(key.capitalize(), val)

        return msg + (Divider.console if print_headers else "")

    def __str__(self) -> str:
        """Return `str(self)`.

        Render a string view of the current board."""
        return self.render(show_guides=True,
                           row_symbols='let', col_symbols='num')


def _test_battleship_board() -> None:
    """Basic tests to check grid creation and rendering."""
    board = BattleshipBoard(height=8, width=8)
    board.show(show_guides=True)

    assert board.grid.shape == (8, 8), f"Unexpected shape: {board.grid.shape}"
    assert np.all(board.grid == board.symbols.EMPTY), "Grid not initialised to empty."

    rendered = board.render(show_guides=True)
    assert isinstance(rendered, str), f"Unexpected type: {type(rendered)}"
    assert "A" in rendered and "0" in rendered, f"Missing row/column headers:"
    assert rendered.count(board.symbols.EMPTY) > 0, "Expected EMPTY spaces in rendering"

    print(CleanText.bf("All tests passed"))


if __name__ == '__main__':
    _test_battleship_board()
