#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file coordinate.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    (Here, place any module-scope constants users will import.)
    
Constants:
    MODULE_LEVEL_CONSTANT1 (int): A module-level constant.

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
        src/battleships/domain/coordinates.py
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
from ast import literal_eval
from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from typing import Annotated, Any, Optional, TypeAlias

# Third-party imports
from pydantic import BeforeValidator

# Local application imports


__all__ = [
    'coordinate_type',
    'Coordinate',
    'CoordinateField']


# Module-level constants
coordinate_type: TypeAlias = tuple[int, int]
"""Type for the ``Coordinate`` class which holds two int-attributes."""


@dataclass(frozen=True, slots=True)
class Coordinate:
    """2D integer coordinate.

    Attributes:
        x:
        y:
    """
    x: int
    y: int

    def __init__(self, x: Any, y: Optional[Any] = None):
        """"""
        if y is not None:
            x_, y_ = self._value_to_int(x), self._value_to_int(y)
        else:
            x_, y_ = self._pair_to_tuple(x)

        object.__setattr__(self, 'x', x_)
        object.__setattr__(self, 'y', y_)

    def as_tuple(self) -> coordinate_type:
        return self.x, self.y

    def __iter__(self):
        yield self.x
        yield self.y

    def __len__(self) -> int:
        # Assumes that `Coordinate` is always created in a valid state
        return 2

    def __getitem__(self, i: int):
        if i == 0:
            return self.x

        if i == 1:
            return self.y

        raise IndexError(i)

    @staticmethod
    def _value_to_int(v: Any) -> int:
        """Safely convert input to ``int``.

        Arguments:
            v:
        """

        if isinstance(v, int):
            return v

        if isinstance(v, str):
            return int(v.strip())

        if isinstance(v, float):
            if not v.is_integer():
                raise ValueError(f"Non-integer float: {v!r}")
            return int(v)

        if hasattr(v, '__index__'):
            # For numpy ints
            return int(v.__index__())

        raise ValueError(f"Value '{v!r}' cannot be cast to 'int'")

    @classmethod
    def _pair_to_tuple(cls, raw: Any) -> coordinate_type:
        """Attempt to construct a ``Coordinate`` from various inputs.

        Arguments:
            raw:
        """
        if isinstance(raw, Coordinate):
            return raw.x, raw.y

        if isinstance(raw, Mapping) and {'x', 'y'} <= raw.keys():
            return cls._value_to_int(raw['x']), cls._value_to_int(raw['y'])

        if isinstance(raw, str):
            out = cls._from_string(raw)
            return out.x, out.y

        if isinstance(raw, (list, tuple)) and len(raw) == 2:
            x, y = raw
            return cls._value_to_int(x), cls._value_to_int(y)

        raise ValueError(f"Unsupported coordinate input: {raw!r}")

    @classmethod
    def _from_string(cls, raw: str) -> 'Coordinate':
        """Parse from a string such as '(x,y)', 'x,y' or '[x,y]'.

        Arguments:
            raw:
        """
        s = raw.strip()

        if s and (s[0] in "([{" and s[-1] in ")]}"):
            val = literal_eval(s)
            return cls._from_iterable(val)

        parts = [p.strip() for p in s.split(',')]
        if len(parts) != 2:
            raise ValueError(f"Invalid Coordinate string: {raw!r}")

        return cls(cls._value_to_int(parts[0]), cls._value_to_int(parts[1]))

    @classmethod
    def _from_iterable(cls, raw: Iterable[Any]) -> 'Coordinate':
        """Convert from iterable of two values such as `(x,y)` and `[x,y]`.

        Arguments:
            raw:
        """
        iterator = iter(raw)

        try:
            first = next(iterator)
            second = next(iterator)
        except StopIteration:
            raise ValueError(f"Expected two elements when building a "
                             f"Coordinate, but got: {raw!r}")

        # Attempting a third next() fails unless there's exactly two elements.
        try:
            next(iterator)
        except StopIteration:
            return cls(cls._value_to_int(first), cls._value_to_int(second))
        else:
            raise ValueError(f"Expected exactly two elements when building a "
                             f"Coordinate, but got: {raw!r}")

    @classmethod
    def coerce(cls, v: Any) -> 'Coordinate':
        """Adapter to convert an input into a valid ``Coordinate``."""
        return v if isinstance(v, Coordinate) else Coordinate(v)

    def __str__(self):
        return f"({self.x}, {self.y})"


CoordinateField: TypeAlias = Annotated[
    Coordinate,
    BeforeValidator(Coordinate.coerce)]
"""Use this alias of `Coordinate` when initialising a `Field` in Pydantic."""
