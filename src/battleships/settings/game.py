#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file game.py)

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
        src/battleships/settings/game.py
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
from .board import BoardSettings
from .fleet import FleetSettings
from .player import PlayerSettings


# Module-level constants

__all__ = ['GameSettings']


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

