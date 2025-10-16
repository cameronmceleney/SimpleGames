#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file battleships.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)

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
        src/battleships/battleships.py
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

# Third-party imports

# Local application imports
from src.battleships.domain.board import Board

# Module-level constants

__all__ = ['Battleships']


class Battleships:
    """Battleships class.

    Attributes:
        x:
    """

    def __init__(self, autoplay: bool = True):
        """"""
        self.x = None
        self._post_init(autoplay=autoplay)

    @staticmethod
    def _post_init(**kwargs):
        if 'autoplay' in kwargs.keys():
            print("Working autoplay.")
            board = Board(length=5, width=5)
            board.show()
            exit()

    def load(self):
        """Load configuration data from yaml file."""
        return

    def play(self):
        """Play a game of battleships."""
        return


if __name__ == '__main__':
    Battleships(autoplay=True)
