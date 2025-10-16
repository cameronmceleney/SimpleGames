#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file player.py)

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
        src/battleships/settings/player.py
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

__all__ = ['PlayerSettings']


class PlayerSettings(BaseModel):
    """Configure player settings that apply before the game begins.

    Attributes:
        shots_limit:    Maximum number of permitted guesses ("shots"), correct
                        or incorrect.

        hot_streak:     Consecutive (alternating turn) correct guesses lead to
                        the player being rewarded by their streak continuing
                        (turn-switching blocked) until their next incorrect
                        guess.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    shots_limit: int = Field(default=40, gt=0)
    hot_streak: int = Field(default=2, gt=1)
