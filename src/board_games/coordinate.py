#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file coordinate.py)

(
Leading paragraphs explaining file in more detail.
)

Attributes:
    
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
from typing import Annotated, Any, NamedTuple, Optional, Self, TypeAlias, Union

# Third-party imports
from pydantic import BeforeValidator

# Local application imports


__all__ = [
    'Point2D',
    'coord_type',
    'CoordLike',
    'value_to_int',
    '_from_iterable',
    '_from_string',
    'pair_to_point2d',
    'Coordinate',
    'CoordinateField']


class Point2D(NamedTuple):
    """Immutable 2D point with attribute and index access.

    Attributes:
        x:
        y:
    """
    # Used `NamedTuple` instead of `dataclass` or `attrs` as ``Point2D``
    # shouldn't be treated like a class! Wanted a `tuple` with attribute and
    # index access.
    x: int
    y: int


coord_type: TypeAlias = tuple[int, int]
"""Canonical grid index type-alias value storage / indexing."""


CoordLike: TypeAlias = Union[
    coord_type,
    'Point2D',
    'Coordinate',
    Mapping[str, Any],
    str
]
"""For function signature that accept any coordinate-like input."""


def value_to_int(v: Any) -> int:
    """Safely convert to ``int``.

    Arguments:
        v:

    Raises:
        ValueError: for non-integers.
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


def _from_iterable(raw: Iterable[Any]) -> 'Point2D':
    """Convert to two values such as `(x,y)` or `[x,y]` to a ``Point2D``..

    Arguments:
        raw:

    Raises:
        ValueError: Unable to build `Point2D` from iterable.
    """
    iterator = iter(raw)

    try:
        first = next(iterator)
        second = next(iterator)
    except StopIteration:
        raise ValueError(f"Expected two elements but got: {raw!r}")

    # Attempting a third next() fails unless there's exactly two elements.
    try:
        next(iterator)
    except StopIteration:
        return Point2D(value_to_int(first), value_to_int(second))
    else:
        raise ValueError(f"Expected exactly two elements but got: {raw!r}")


def _from_string(raw: str) -> 'Point2D':
    """Return a ``Point2D`` by parsing a string such as '(x,y)', 'x,y' or '[x,y]'.

    Arguments:
        raw:

    Raises:
        ValueError: Unable to build `Point2D` from given string.
    """
    s = raw.strip()

    if s and (s[0] in "([{" and s[-1] in ")]}"):
        val = literal_eval(s)
        return _from_iterable(val)

    parts = [p.strip() for p in s.split(',')]
    if len(parts) != 2:
        raise ValueError(f"Invalid Coordinate string: {raw!r}")

    return Point2D(value_to_int(parts[0]), value_to_int(parts[1]))


def pair_to_point2d(raw: Any) -> 'Point2D':
    """Attempt to construct a ``Coordinate`` from various inputs.

    Arguments:
        raw:
    """
    if isinstance(raw, Coordinate):
        return Point2D(raw.x, raw.y)

    if isinstance(raw, Point2D):
        return raw

    if isinstance(raw, Mapping) and {'x', 'y'} <= raw.keys():
        return Point2D(value_to_int(raw['x']),
                       value_to_int(raw['y']))

    if isinstance(raw, str):
        return _from_string(raw)

    if isinstance(raw, (list, tuple)) and len(raw) == 2:
        return Point2D(value_to_int(raw[0]),
                       value_to_int(raw[1]))

    raise ValueError(f"Unsupported coordinate input: {raw!r}")


@dataclass(frozen=True, slots=True)
class Coordinate:
    """2D integer coordinate.

    Has strict construction and convenient views.

    Attributes:
        x:
        y:
    """
    x: int
    y: int

    def __init__(self, x: Any, y: Optional[Any] = None):
        if y is not None:
            x_, y_ = value_to_int(x), value_to_int(y)
        else:
            p = pair_to_point2d(x)
            x_, y_ = p.x, p.y

        object.__setattr__(self, 'x', x_)
        object.__setattr__(self, 'y', y_)

    def as_xy(self) -> 'coord_type':
        """Return as ``(x,y)``"""
        return self.x, self.y

    def as_tuple(self) -> 'coord_type':
        """Return as ``(x,y)``.

        For backwards compatibility.
        """
        return self.as_xy()

    def as_point(self) -> 'Point2D':
        """Return as Point2D for accesses by attribute or index downstream."""
        return Point2D(self.x, self.y)

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

    @classmethod
    def from_point(cls, p: 'Point2D') -> Self:
        return cls(p.x, p.y)

    @classmethod
    def from_xy(cls, xy: coord_type) -> Self:
        return cls(xy)

    @classmethod
    def coerce(cls, v: Any) -> Self:
        """Adapter to convert an input into a valid ``Coordinate``."""
        return v if isinstance(v, Coordinate) else Coordinate(v)

    def __str__(self):
        return f"({self.x}, {self.y})"


CoordinateField: TypeAlias = Annotated[
    Coordinate,
    BeforeValidator(Coordinate.coerce)]
"""Pydantic field alias of ``Coordinate``."""
