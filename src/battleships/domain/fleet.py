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

Todo:

References:
    Style guide: `Google Python Style Guide`_

Notes:
    File version
        0.1.0
    Project
        SimpleGames
    Path
        src/battleships/domain/fleet.py
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
from typing import Any, Mapping

# Third-party imports
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    ValidationInfo, computed_field)

# Local application imports
from src.battleships.domain.ship import ShipSpec

# Module-level constants

__all__ = ['Fleet']


class Roster(BaseModel):
    """Named set of ship specs."""
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    roster: dict[str, ShipSpec] = Field(default_factory=dict)

    @classmethod
    def from_rosters_yaml(cls, id_: str, root: Mapping[str, Any]) -> "Roster":
        """"""
        node = root.get(id_)
        if node is None or "roster" not in node:
            raise KeyError(f"Roster id [{id_} not found.")

        return cls(id=id_, roster=node["roster"])


class Fleet(BaseModel):
    """All ships used by a player during a game of Battleships.

    A fleet is a set of ship types.

    Attributes:
        id:             Unique tag for this fleet.

        roster:         All ships used by this fleet.

        counts:         Number of each ship type.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    ships: dict[str, tuple[int, int]] = Field(default_factory=dict)
    roster: Roster = Field(default_factory=Roster)
    counts: dict[str, int] = Field(default_factory=dict, gt=0)

    @model_validator(mode='after')
    def _validate_roster_counts(self, info: ValidationInfo) -> "Fleet":
        """Validate this Fleet against global FleetSettings instance.

        Ensures global settings are applied to a player's game configuration
        prior to the game beginning.

        FleetSettings are provided to this method using Pydantic's context
        helpers. If no context is provided, a factory injects it.

        Attributes:
            info:               Context from the `FleetSettings` instance.
        """
        unknown = [k for k in self.counts if k not in self.roster]
        if unknown:
            raise ValueError(f"'counts' references unknown ship "
                             f"type: {unknown}")

        context = info.context or {}
        settings = context.get("fleet_settings")

        if settings is None:
            raise AttributeError(f"'FleetSettings' were not provided")

        if self.total_ships > settings.max_ships:
            raise ValueError(
                f"More ships [{self.total_ships}] than the maximum "
                f"[{settings.max_ships}] permitted."
                f" Your requested fleet '{self.id}' contained:\n\n{self.ships} ")

        return self

    @computed_field
    def total_ships(self) -> int:
        return sum(self.counts.values())

    def count(self, name: str) -> int:
        """"""
        return self.counts.get(name, 0)

    @classmethod
    def create(cls, *, settings, **fleet_kwargs) -> "Fleet":
        """Construct and validate a Fleet against FleetSettings."""

        return cls.model_validate(fleet_kwargs,
                                  context={"fleet_settings": settings})
