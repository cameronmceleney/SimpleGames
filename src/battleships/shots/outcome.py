#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file outcome.py)

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
from enum import StrEnum

# Third-party imports

# Local application imports

# Module-level constants


__all__ = ['Outcome']


class Outcome(StrEnum):
    """Possible outcomes of a shot at a valid Coordinate.

    Attributes:
        HIT: Successful shot.
        MISS: Unsuccessful shot.
        REPEAT: Take another shot.
        OUT: Out-of-bounds.
        INVALID: Coordinates were invalid.
        ERROR: Error encountered.
    """

    # Members: name becomes a human label (str), e.g. "Hit"
    HIT = "Hit! You struck an enemy ship."
    MISS = "Miss. Nothing struck."
    REPEAT = "You've already targeted that cell."
    OUT = "Shot is out of bounds."
    INVALID = "Coordinate input was invalid."
    ERROR = "Error encountered."

    def __new__(cls, message: str):
        obj = str.__new__(cls, message)
        obj._value_ = str(message)

        return obj

    def __str__(self) -> str:
        return self.name.capitalize().replace("_", " ")

    @property
    def message(self) -> str:
        """Verbose description of the outcome.

        Alias for the value of the Enum member.
        """
        return self._value_
