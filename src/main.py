#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file main.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of main.py). Note that leading symbol '>>>' includes the 
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
        src/main.py
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

# Third-party imports

# Local application imports
from battleships.gameplay.game import test_battleships

# Module-level constants


if __name__ == "__main__":
    test_battleships()
