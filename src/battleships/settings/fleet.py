#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file fleet.py)

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
        src/battleships/settings/fleet.py
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

__all__ = ['FleetSettings']


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
