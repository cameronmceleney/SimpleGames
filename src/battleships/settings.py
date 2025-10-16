#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file settings.py)

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
        src/battleships/settings.py
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

__all__ = ['FleetSettings', 'BoardSettings', 'PlayerSettings', 'GameSettings']


class FleetSettings(BaseModel):
    """Configure fleet (i.e. "ship") settings.

    Attributes:
        max_ships:
            Maximum number of ships in this fleet instance.

        can_place_only_horizontal:
            Ships can be solely oriented along x-axis.

        can_place_only_vertical:
            Ships can be solely oriented along y-axis.

        can_place_along_strict_diagonal:
            Ships can be placed along diagonals. A *strict* diagonal implies
            that a cruiser (length: three) could be placed along ``(A1,B2,C3)``
            but not ``(A1,B1,C2)``.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    max_ships: int = Field(10, gt=0)

    can_place_only_horizontal: bool = True
    can_place_only_vertical: bool = True
    can_place_along_strict_diagonal: bool = False


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


class GameSettings(BaseModel):
    """Container for all settings.

    Attributes:
        Board: See BoardSettings.
        Player: See PlayerSettings.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    Fleet: FleetSettings = Field(default_factory=FleetSettings)
    Board: BoardSettings = Field(default_factory=BoardSettings)
    Player: PlayerSettings = Field(default_factory=PlayerSettings)
