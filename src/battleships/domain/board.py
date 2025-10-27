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
import os
from typing import Any, ClassVar, Optional, Type

# Third-party imports
import numpy as np


# Local application imports
from src.battleships.settings import BoardSettings
from src.battleships.domain.fleet import Fleet
from src.battleships.domain.ship import Ship
from src.utils.utils import CleanText, Divider, JustifyText
from src.battleships.domain.coordinate import Coordinate
from src.battleships.domain.position import Position


# Module-level constants
class Symbols(StrEnum):
    """Symbols to denote ships and actions on the playing board."""
    EMPTY = ' '
    HIT = '#'
    MISS = '/'
    VERTICAL_DIVIDER = '-'
    HORIZONTAL_DIVIDER = '|'

    # Aliases
    space = EMPTY
    vd = VERTICAL_DIVIDER
    hd = HORIZONTAL_DIVIDER


__all__ = ['Board']


@dataclass
class Board:
    """2D game board."""
    length: int
    width: int
    grid: np.ndarray = field(init=False, repr=False)

    _symbols: ClassVar[Type[Symbols]] = Symbols

    def __post_init__(self):
        """Initialise grid after dataclass is constructed."""
        # Initial grid of zeros is easily created using `reset` method.
        self.grid = self.reset_grid()

    def reset_grid(self, inplace: bool = False) -> Optional[np.ndarray]:
        """Create a zeroed grid.

        Arguments:
            inplace: If `True`, update ``self.grid``. Otherwise, return a new grid.
        """
        grid = np.full(shape=(self.length, self.width),
                       fill_value=self._symbols.EMPTY,
                       dtype='U1')

        if inplace:
            self.grid = grid
            return None

        return grid

    def clone(self) -> "Board":
        """Clone a board."""
        b = Board(self.length, self.width)
        b.grid = self.grid.copy()
        return b

    def show(self, has_dividers: bool = True) -> None:
        """Print the current grid-state."""
        output: str = "\n"
        _horizontal_line = f"{self._symbols.vd * (self.width * 2 + 2)}\n"

        if has_dividers:
            indent = f"{' ' * 4}"
        else:
            indent = f"{' ' * 2}"

        col_nums: str = '' + indent

        for c, row in enumerate(self.grid):
            output += CleanText.bf(chr(65 + c)) + self._symbols.space
            col_nums += CleanText.bf(c) + self._symbols.space

            if has_dividers:
                output += self._symbols.hd + self._symbols.space

            for sym in row:
                output += str(sym) + ' '
            output += '\n'

        if has_dividers:
            dividers = " ".join([self._symbols.vd for _ in range(0, self.length)])
            output += indent + dividers + '\n'

        output += col_nums + '\n'

        print(output)

    def add_shot(self, shot: Any) -> "Coordinate | None":
        """Safely load a shot onto the game board.

        Only add a shot if the following conditions are true for the targeted
        tile:
            - it's empty, or
            - it's occupied by an unhit shit tile.
        """
        coord = Coordinate.coerce(shot)

        self.grid[coord] = self._symbols.HIT
        self.show(has_dividers=False)
        return coord

    def add_ship(self, *ship: Ship | Position) -> None:
        """Load a ship onto the game board.

        Can take any number of ships.

        Arguments:
            ship:           Ship to load.
        """
        for s in ship:
            if isinstance(s, Ship):
                self.add_guess(s.pos, s.type[0].upper())
            if isinstance(s, Position):
                self.add_guess(s, 'S')

    def add_guess(self, coord: Coord | Placement, symbol: str = 'T'):
        """Add a guess to the game board."""
        if isinstance(coord, type(Coord)):
            self.grid[coord] = symbol
            return

        if isinstance(coord, Placement):
            for pos in coord.positions:
                self.grid[pos] = symbol
            return

    def __str__(self, print_headers: bool = True):

        msg = Divider.console if print_headers else ""
        msg += Divider.console.make_title('Board')

        for key, val in self.__dict__.items():
            if key == 'grid' or key[0] == '_':
                continue
            msg += JustifyText.kv(key.capitalize(), val)

        return msg + (Divider.console if print_headers else "")
