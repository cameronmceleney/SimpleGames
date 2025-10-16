#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file board.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)

(
Trailing paragraphs summarising final details.
)

References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/battleships/settings/board.py
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
from pydantic import BaseModel, ConfigDict, Field

# Third-party imports

# Local application imports

# Module-level constants

__all__ = ['BoardSettings']


class BoardSettings(BaseModel):
    """Configure board (i.e. "grid") settings.

    Attributes:
        width:          X-axis (horizontal) bounds.

        height:         Y-axis (vertical) bounds.

        max_players:    Number of players in the game.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    width: int = Field(default=10, gt=0)
    height: int = Field(default=10, gt=0)
    max_players: int = Field(default=2, ge=2)
