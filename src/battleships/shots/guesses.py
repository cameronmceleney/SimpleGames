#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file guesses.py)

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
        src/battleships/domain/guesses.py
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
from collections.abc import Iterable
from typing import Any

# Third-party imports
from pydantic.dataclasses import dataclass
from pydantic import Field, field_validator, model_validator

# Local application imports
from battleships.shots.shot_info import Shots, ShotInfo

# Module-level constants
"""A module-level constant with in-line docstring."""

__all__ = ['Guesses']


@dataclass
class Guesses:
    """Container for players guessed shots.

    Note:
        Don't cache key internal attributes such as ``misses``, ``hits``, and
        ``total`` as this could lead to stale counters. Instead, compute these
        numbers on-demand by creating *properties* for each.

    Attributes:
        shots:              Previously guessed coordinates.
    """
    shots: "Shots" = Field(default_factory=list)

    @field_validator('shots', mode='before')
    @classmethod
    def _coerce_shots(cls, v: Any) -> "Shots":
        """Missing description.

        Accepts:
            - iterable of ``ShotInfo``.
            - iterable of raw coordinates (``Coordinate`` and ``str``/``list``/``tuple``)
        """
        if v is None:
            return []

        # Anything that is an object-of-shots then use it
        seq = getattr(v, "shots", v)

        # Treat single strings as one shot (not sequence of characters)
        if isinstance(seq, str):
            seq = [seq]

        try:
            iterator = iter(seq)
        except TypeError:
            raise TypeError("Shots must be iterable.")

        out: 'Shots' = []
        for item in iterator:
            out.append(item
                       if isinstance(item, ShotInfo)
                       else ShotInfo.from_shot(item))

        return out

    @model_validator(mode='after')
    def _ensure_types(self) -> 'Guesses':
        """Ensures iterable only contains ``ShotInfo`` objects."""
        if not all(isinstance(s, ShotInfo) for s in self.shots):
            raise TypeError("'self.shots' must only contain 'ShotInfo' objects.")

        return self

    @staticmethod
    def parse_shot(s: Any) -> 'ShotInfo':
        """Helper"""
        shot_info = ShotInfo.from_shot(s)

        if shot_info is None:
            raise ValueError(f"Invalid shot: {s!r}")

        return shot_info

    @classmethod
    def parse_shots(cls, shots: Iterable[Any]) -> "Shots":
        """Helper to load multiple shots."""
        return [cls.parse_shot(s) for s in shots]

    def append(self, s: Any) -> 'ShotInfo':
        """"""
        shot = s if isinstance(s, ShotInfo) else self.parse_shot(s)
        self.shots.append(shot)
        return shot

    @property
    def hits(self) -> int:
        return sum(s.has_hit is True for s in self.shots)

    @property
    def misses(self) -> int:
        return sum(s.has_hit is False for s in self.shots)

    @property
    def total(self) -> int:
        return len(self.shots)
