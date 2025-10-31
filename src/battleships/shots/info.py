#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file info.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)

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
        src/battleships/domain/shot_info.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        24 Oct 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
from typing import Optional, TypeAlias

# Third-party imports
from pydantic import BaseModel, ConfigDict

# Local application imports
from board_games import Coordinate
from battleships.shots import Outcome

# Module-level constants

__all__ = ['Shots', 'Info']


class Info(BaseModel):
    """Key information about each guess.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)
    coord: Coordinate
    outcome: Outcome
    ship_type: Optional[str] = None
    ship_index: Optional[int] = None
    repeat: bool = False


Shots: TypeAlias = list['Info']
"""Description missing."""
