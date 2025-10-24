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
from collections import Counter
from typing import Any, Mapping

# Third-party imports
from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    model_validator,
    ValidationInfo, computed_field, PrivateAttr)

# Local application imports
from src.battleships.domain.ship import ShipSpec, Ship
from src.utils.utils import load_yaml, JUST_L_WIDTH, CONSOLE_DIVIDER
from src.log import get_logger

log = get_logger(__name__)

__all__ = ['Fleet']


# Module-level constants


class Roster(BaseModel):
    """Named set of ship specs.

    Used to build a `Fleet`.

    Attributes:
        id:           Unique ID given to this roster in *rosters.yml*.

        ships:              All uninitialised `ShipSpecs`.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    ships: dict[str, ShipSpec] = Field(default_factory=dict)

    @classmethod
    def load_from_yaml(cls, id_: str, *, filepath: str = "config/rosters.yml") -> 'Roster':
        """Load a roster from the YAML configuration file.

        The shape of each entry in the roster file should be:
            <id>:
                roster:
                    <name>: ship spec entries...

        TODO:
            - Update this method to generate a `ShipSpec` as it doesn't set `ShipSpec.type`.
        """
        cls.id = id_
        roster_yaml = load_yaml(filepath)
        #log.info(f"Roster | load_from_yaml({id_})\n{'-'*16}\n{root}\n\n")

        try:
            root = roster_yaml.get(id_)
        except KeyError as e:
            raise f"Couldn't find this id {id_}."
        else:
            ship_nodes = root['roster']

        ships = {}
        for name, spec in ship_nodes.items():
            ships[name] = ShipSpec(**spec)

        return cls(id=id_, ships=ships)

    def __str__(self):
        msg = (f"{CONSOLE_DIVIDER}"
               f"<Roster> '{self.id}'\n"
               f"{CONSOLE_DIVIDER}")

        for k, val in self.ships.items():
            key = "'" + k + "'"
            msg += f"{key:<{JUST_L_WIDTH}} {val.__repr__()}\n"

        msg += f"{CONSOLE_DIVIDER}"

        return msg


class Fleet(BaseModel):
    """All ships used by a player during a game of Battleships.

    A fleet is a set of ship types.

    Attributes:
        id:             Unique tag for this fleet.

        ships:         All ships used by this fleet.

        counts:         Number of each ship type.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    ships: dict[str, Ship] = Field(default_factory=dict)
    roster: Roster = Field(default_factory=lambda r: Roster(id=''))
    counts: dict[str, int] = Field(default_factory=dict, init=False, repr=False)

    _remaining_tiles: int = 0

    @property
    def is_alive(self) -> bool:
        """Check if this fleet has at least one remaining tile to be sunk."""
        return True if self._remaining_tiles > 0 else False

    @classmethod
    def load_from_yaml(
            cls,
            *,
            fleet_id: str,
            fleet_filepath: str = "config/fleet.yml",
            settings=None
    ) -> 'Fleet':
        """Load a fleet from the YAML configuration file.

        Shape of each entry in the fleet YAML file should be:
            roster: <id>
            ships:
                <name>: {ship spec entries...}

        Arguments:
            fleet_id:           Text.

            fleet_filepath:     Text.

            settings:           Game settings (not yet implemented)
        """

        fleet_config = load_yaml(fleet_filepath)
        fleet_props = fleet_config.get(fleet_id)

        raw_counts = fleet_props.get('ships', {})
        counts = {name: int(node.get('quantity')) for name, node in raw_counts.items()}

        roster = Roster.load_from_yaml(id_=fleet_props.get('roster'))
        log.debug(roster.ships)

        ships: dict[str, Ship] = {}

        for ship_type, spec in roster.ships.items():
            quantity = counts.get(ship_type, 0)
            for q in range(quantity):
                key = f"{ship_type}_{q}"
                ships[key] = Ship(spec=spec, type=ship_type)

        return cls.model_validate({'id': fleet_id,
                                   'ships': ships,
                                   'roster': roster,
                                   'counts': counts},
                                  context=settings)

    def apply_player_positions(self, player_data: Mapping[str, Any]) -> None:
        """"""
        track_counts = {t: 0 for t in self.counts}

        for ship_type, node in player_data.items():
            if ship_type not in self.counts:
                raise ValueError(f"Unknown ship type: {ship_type}")

            if "position" in node:
                raw_list = node["position"]
            elif "positions" in node:
                raw_list = node["positions"]
            else:
                raise ValueError(f"{ship_type}: missing positions.")

            for raw in raw_list:
                idx = track_counts[ship_type]
                if idx >= self.counts[ship_type]:
                    raise ValueError(f"Too many positions for ship type: {ship_type}.")

                key = f"{ship_type}_{idx}"
                self.ships[key].update_position(raw)
                track_counts[ship_type] += 1

        missing = [t for t, need in self.counts.items() if track_counts.get(t, 0) != need]
        if missing:
            raise ValueError(f"Missing positions for ship type: {', '.join(missing)}")

    def __call__(self, ship: str) -> Ship:
        return self.ships[ship]

    def __str__(self, print_headers: bool = True):

        msg = ""
        if print_headers:
            msg += f"{CONSOLE_DIVIDER}"

        msg += f"<Fleet> '{self.id}'\n"
        msg += f"{CONSOLE_DIVIDER}"

        for k, val in self.ships.items():
            key = "'" + k + "'"
            msg += f"{key:<{JUST_L_WIDTH}} {val.__repr__()}\n"

        if print_headers:
            msg += f"{CONSOLE_DIVIDER}"

        return msg


