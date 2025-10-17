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
ROSTERS_FILE_PATH = "config/rosters.yml"
FLEET_FILE_PATH = "config/fleet.yml"


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
    def load_from_yaml(cls, id_: str, *, filepath: str = ROSTERS_FILE_PATH) -> 'Roster':
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

    _roster_id: str | None = PrivateAttr(default=None)

    @classmethod
    def load_from_yaml(
            cls,
            fleet_id: str,
            *,
            fleet_filepath: str = FLEET_FILE_PATH,
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

        config_data = load_yaml(fleet_filepath)
        fleet_props = config_data.get(fleet_id)
        log.debug(fleet_props)

        roster = Roster.load_from_yaml(id_=fleet_props.get('roster'))
        log.debug(roster.ships)

        ships: dict[str, Ship] = {}

        for name, spec in roster.ships.items():
            quantity = int(fleet_props.get('ships').get(name).get('quantity'))
            for q in range(0, quantity):
                ships[name + f'_{q}'] = Ship(spec=spec)

        return cls.model_validate({'id': fleet_id,
                                   'ships': ships,
                                   '_roster_id': roster.id},
                                  context=settings)

    def __str__(self, headers: bool = True):

        msg = ""
        if headers:
            msg += f"{CONSOLE_DIVIDER}"

        msg += f"<Fleet> '{self.id}'\n"
        msg += f"{CONSOLE_DIVIDER}"

        for k, val in self.ships.items():
            key = "'" + k + "'"
            msg += f"{key:<{JUST_L_WIDTH}} {val.__repr__()}\n"

        if headers:
            msg += f"{CONSOLE_DIVIDER}"

        return msg


