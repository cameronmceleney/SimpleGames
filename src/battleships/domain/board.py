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
import numpy as np
from typing import Optional

# Third-party imports

# Local application imports
from src.battleships.settings import BoardSettings
from src.battleships.domain.fleet import Fleet

# Module-level constants

__all__ = ['Board']


@dataclass
class Board:
    """2D game board."""
    length: int
    width: int
    grid: np.ndarray = field(init=False, repr=False)

    _has_loaded_fleet: bool = field(default=False, init=False, repr=False)

    def __post_init__(self):
        """Initialise grid after dataclass is constructed."""
        # Initial grid of zeros is easily created using `reset` method.
        self.grid = self.reset_grid()

    def reset_grid(self, inplace: bool = False) -> Optional[np.ndarray]:
        """Create a zeroed grid.

        Arguments:
            inplace: If `True`, update ``self.grid``. Otherwise, return a new grid.
        """
        grid = np.zeros((self.length, self.width), dtype=int)

        if inplace:
            self.grid = grid
            return None
        else:
            return grid

    def show(self) -> None:
        """Print the current grid-state."""
        for row in self.grid:
            print(' '.join(map(str, row)))
        return

    def add_fleet(self, fleet: Fleet):
        """Load a fleet onto the board."""

        if self._has_loaded_fleet:
            raise RuntimeError(f"A fleet has already been loaded onto this "
                               f"board.")

        for ship in fleet.roster.items():






