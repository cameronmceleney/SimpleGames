#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file grid.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of grid.py). Note that leading symbol '>>>' includes the 
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
        src/battleships/board/grid.py
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
from dataclasses import field
from typing import ClassVar, Optional, Self, Type

# Third-party imports
import numpy as np
from pydantic.dataclasses import dataclass

# Local application imports
from .symbols import SymbolsProto, DefaultSymbols


@dataclass(slots=True)
class Grid:
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
        g = Grid(height=self.height, width=self.width)
        g.grid = self.grid.copy()
        return g
