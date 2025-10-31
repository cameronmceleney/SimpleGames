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
from typing import Any, Literal

# Third-party imports
import numpy as np
from pydantic.dataclasses import dataclass

# Local application imports
from board_games import Board as BaseBoard, Coordinate
from battleships.ships import Position
from utils import CleanText, Divider, JustifyText

from .symbols import Symbols


@dataclass(slots=True)
class Board(BaseBoard):
    """2D battleship game board as a grid of mutable characters.

    This class contains high-level helpers specific to Battleships games.
    """
    symbols = Symbols

    def mark_hit(self, c: Any) -> None:
        """Apply HIT glyph."""
        self.set(c, self.symbols.HIT)

    def mark_damage(self, c: Any) -> None:
        """Mark ship damage by turning character to lowercase."""
        coord = Coordinate.coerce(c)
        self.require_in_bounds(coord)
        ch = self.get(coord)
        if isinstance(chr, str) and len(chr) == 1 and ch.isalpha():
            self.set(coord, ch.lower())

    def mark_miss(self, c: Any) -> None:
        """Apply MISS glyph."""
        self.set(c, self.symbols.MISS)

    def is_marked(self, c: Any) -> bool:
        v = self.get(c)
        return v in (self.symbols.HIT, self.symbols.MISS)

    def place(self, pos: Any, symbol: str = 'S') -> None:
        """Place a multi-cell object onto the board.

        To place a ship do ``obj.place(ship.position, ship.symbol)``.
        """
        p = Position.coerce(pos)

        for coord in p.positions:
            self.set(coord, symbol)

    def _opponent_mask(self, ch: str) -> str:
        """Show hits and missed."""
        if ch in (self.symbols.HIT, self.symbols.MISS):
            return ch
        else:
            return self.symbols.EMPTY

    def show(
            self,
            *,
            mode: Literal['self', 'opponent'] = 'self',
            show_guides: bool = True
    ) -> None:
        match mode:
            case 'self':
                output = self.render(show_guides=show_guides,
                                     row_symbols='let', col_symbols='num')
            case 'opponent':
                output = self.render_with_mask(self._opponent_mask,
                                               show_guides=show_guides,
                                               row_symbols='let',
                                               col_symbols='num')
            case _:
                raise NotImplementedError("Attempted to use unsupported key.")

        print(output)

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
    board = Board(height=8, width=8)
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
