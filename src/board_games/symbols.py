#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file symbols.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

Examples:
    (Here, place useful implementations of the contents of symbols.py). Note that leading symbol '>>>' includes the 
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
        src/board_games/symbols.py
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
from typing import Protocol

# Third-party imports

# Local application imports

# Module-level constants

__all__ = ['SymbolsProto', 'DefaultSymbols']


class SymbolsProto(Protocol):
    EMPTY: str


class DefaultSymbols:
    EMPTY: str = ' '
