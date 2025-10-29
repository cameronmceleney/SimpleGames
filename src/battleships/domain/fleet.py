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
from typing import Any, Mapping, Optional

# Third-party imports
from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    Field,
    model_validator, PrivateAttr, )
from yaml import YAMLError

# Local application imports
from src.battleships.domain.ship import ShipSpec, Ship
from src.utils.utils import load_yaml, JustifyText, Divider
from src.log import get_logger

log = get_logger(__name__)

__all__ = ['Fleet']


# Module-level constants


class Roster(BaseModel):
    """Named set of ship specs loaded from a configuration file.

    Used to build a `Fleet`.

    Expected shape of the configuration file:
        <id>:
            <roster>:
                <ship_type>: { size: <int>, is_cloaded: <bool, optional> }

    Attributes:
        id:           Unique ID given to this roster in *rosters.yml*.

        ships:              All uninitialised `ShipSpecs`.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    ships: dict[str, ShipSpec] = Field(default_factory=dict)

    _raw_counts: Optional[Mapping[str, int]] = PrivateAttr(default=None)

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
        data = load_yaml(filepath)
        node = data.get(id_)

        if node is None:
            raise KeyError(f"Roster ID '{id_!r}' wasn't found at '{filepath!r}'")

        if 'roster' not in node or not isinstance(node['roster'], Mapping):
            raise YAMLError(f"Roster id '{id_!r}' must contain a mapping"
                            f"under the 'roster' key.")

        ships: dict[str, ShipSpec] = {}
        for name, ship_spec_node in node['roster'].items():
            if not isinstance(ship_spec_node, Mapping):
                raise YAMLError(f"Roster ID '{id_!r}' entry '{name!r}' must be"
                                f"a mapping of valid 'ShipSpec' fields.")
            else:
                ships[name] = ShipSpec(type_name=name, **ship_spec_node)

        return cls(id=id_, ships=ships)

    @computed_field
    @property
    def counts(self) -> dict[str, int]:
        if self._raw_counts is None:
            return {}

        return {t: int(self._raw_counts.get(t, 0)) for t in self.ships.keys()}

    def __str__(self):
        return f"{self.__class__.__name__}(id={self.id}, ships={self.ships})"

    def __repr__(self) -> str:
        msg = Divider.section.make_title('Roster', self.id, wrap=True)
        for type_, spec_ in self.ships.items():
            msg += JustifyText.kv(f"'{type_}'", spec_, value_repr=True)

        return msg + Divider.console


class Fleet(BaseModel):
    """All ships used by a player in Battleships.

    A fleet is a set of ship types.

    Expected shape of the configuration file:
        <fleet_id>:
            roster: <roster_id>
            ships:
            <ship_type>: { quantity: <int> }

    Attributes:
        id: Unique identifier for this fleet.
        roster: Roster used to instance fleet's ``ShipSpec``.
        ships: Concrete ``Ship`` objects keyed as `<type>_<index>`.
        counts: Quantities for each ship type.

    TODO:
        - Add explicit model validator so `load_from_yaml` can just return `cls`
        - Turn `_remaining_tiles` into a computed file that is decremented whenever a hit is registered.
        - Split `Fleet.load_from_yaml()` into smaller, more meaningful methods (private and/or public)
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    roster: Roster
    ships: dict[str, Ship] = Field(default_factory=dict)
    counts: dict[str, int] = Field(default_factory=dict)

    @model_validator(mode='after')
    def _check_counts_against_roster(self) -> 'Fleet':
        """Ensure counts reference only known roster types and ship counts match."""
        unknown = [s for s in self.counts if s not in self.roster.ships]
        if unknown:
            raise ValueError(f"<{self.__class__.__name__}> 'counts'"
                             f"references unknown ship types: {unknown!r}")

        # Check loading of `Ship`
        expected_total = sum(self.counts.values())
        loaded_total = len(self.ships)
        if loaded_total != expected_total:
            raise ValueError(f"<{self.__class__.__name__}.{self.id!r}> "
                             f"loaded [{loaded_total}] ships "
                             f"but counts sum to [{expected_total}].")

        # Check loading of each type
        per_type = {}
        for k, ship in self.ships.items():
            per_type[ship.type] = per_type.get(ship.type, 0) + 1

        for type_, required_quantity in self.counts.items():
            loaded_counts = per_type.get(type_, 0)
            if loaded_counts != required_quantity:
                raise ValueError(f"<{self.__class__.__name__}.{self.id!r}> "
                                 f"loaded '{loaded_counts}' of '{type_}' "
                                 f"but counts expected are "
                                 f"[{required_quantity}].")

        return self

    @property
    def remaining_tiles(self) -> int:
        """The total number of tiles still alive within this fleet."""
        return sum(getattr(s, 'remaining_tiles', 0)
                   for s in self.ships.values())

    @property
    def is_alive(self) -> bool:
        """Check if this fleet has at least one remaining tile to be sunk."""
        return self.remaining_tiles > 0

    @property
    def total_ships(self) -> int:
        return sum(self.counts.values())

    def by_type(self, ship_type: str) -> list[Ship]:
        """All ships of a type in index order."""
        return [self.ships[f"{ship_type}_{i}"]
                for i in range(self.counts.get(ship_type, 0))]

    def placed_ships(self) -> list[str]:
        return [t for t, s in self.ships.items() if s.placement is not None]

    def unplaced_ships(self) -> list[str]:
        return [t for t, s in self.ships.items() if s.placement is None]

    @classmethod
    def load_from_yaml(
            cls,
            *,
            fleet_id: str,
            roster_filepath: str = 'config/rosters.yml',
            fleet_filepath: str = "config/fleet.yml",
            settings: Optional[Any] = None
    ) -> 'Fleet':
        """Load a fleet from the YAML configuration file.

        Arguments:
            fleet_id: Fleet identifier; top-level key from the configuration file.
            roster_filepath: Relative path to the configuration file.
            fleet_filepath: Relative path to the configuration file.
            settings: Game settings (not yet implemented)
        """
        # Extract target fleet from the configuration file
        fleets = load_yaml(fleet_filepath)
        log.debug(fleets.items())

        fleet_node = fleets.get(fleet_id)
        if fleet_node is None:
            raise YAMLError(f"Flet id '{fleet_id!r}' wasn't found at '{fleet_filepath}'.")

        roster_id = fleet_node.get('roster')
        if not roster_id:
            raise ValueError(f"Fleet '{fleet_id!r}' is missing a 'roster' key.")

        # Load roster and quantities of each ship from the configuration files.
        roster = Roster.load_from_yaml(roster_id, filepath=roster_filepath)
        log.debug(roster.ships)

        raw_ship_counts = fleet_node.get('ships', {})
        if not isinstance(raw_ship_counts, Mapping):
            raise YAMLError("'Ship' keys must be mappings from "
                            "<ship_type: { quantity: <int> }>")
        log.debug(raw_ship_counts)

        counts: dict[str, int] = {}
        for name, node in raw_ship_counts.items():
            quantity = int(node.get('quantity'))
            if quantity < 0:
                raise YAMLError(f"<Fleet> <{fleet_id!r}.{name!r}> "
                                f"Ship has a missing/invalid quantity.")

            counts[name] = quantity

        # Build each `Ship` object from roster.yml + fleet.yml config files.
        ships: dict[str, Ship] = {}

        for ship_type, ship_spec in roster.ships.items():
            for i in range(counts.get(ship_type, 0)):
                key = f"{ship_type}_{i}"
                ships[key] = Ship(spec=ship_spec, index=i)

        return cls.model_validate({'id': fleet_id, 'roster': roster,
                                   'ships': ships, 'counts': counts},
                                  context=settings)

    def apply_placements(self, player_data: Mapping[str, Any]) -> None:
        """Attach placements to each ship from a player's mapping.

        Expected shape for each ship-type in the configuration files:
            <ship_type>:
                position: <coords-like>

        Arguments:
            player_data:
        """
        # Track placements per ship_type that have been used
        for ship_type, node in player_data.items():
            if ship_type not in self.counts:
                raise ValueError(f"Unknown ship type in player data: "
                                 f"{ship_type!r}")

            if not isinstance(node, Mapping):
                raise ValueError(f"<{ship_type!r}> entry my be a mapping, "
                                 f"got '{type(node)}'.")

            # Don't peek at positional data. Instead pass the raw YAML onto
            # each Ship and let them extract their data. We know that each Ship
            # in targets is ordered, so we can infer that the 0th entry of
            # `targets` should read the first valid positional line in
            # `raw_node`
            for ship in self.by_type(ship_type):
                ship.load_placement(node)

        # placed_ships: dict[str, int] = {key: 0 for key in self.counts}
        #
        # for ship_type, node in player_data.items():
        #     if ship_type not in self.counts:
        #         raise ValueError(f"Unknown ship type in player data: "
        #                          f"{ship_type!r}")
        #
        #     if not isinstance(node, Mapping):
        #         raise YAMLError(f"'{ship_type!r}' entry must be a mapping.")
        #
        #     seq = node.get('position')
        #     if seq is None: seq = node.get('positions')
        #
        #     for item in seq:
        #         idx = placed_ships[ship_type]
        #         if idx >= self.counts[ship_type]:
        #             raise ValueError(f"Too many ships of the same type.")
        #
        #         key = f"{ship_type}_{idx}"
        #         self.ships[key].load_placement(item)
        #         placed_ships[ship_type] += 1
        #
        # # Ensure all declared `Ship`s have a placement
        # missing = [t for t, need in self.counts.items()
        #            if placed_ships.get(t, 0) != need]
        #
        # if missing:
        #     raise ValueError(f"Missing positions for ship type(s): "
        #                      f"{', '.join(missing)!r}")

    def __call__(self, ship_name: str) -> Ship:
        return self.ships[ship_name]

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}.{self.id!r}>"

    def __repr__(self, print_headers: bool = True):

        msg = Divider.console if print_headers else ''
        msg += Divider.console.make_title('Fleet', self.id)

        for k, val in self.ships.items():
            msg += JustifyText.kv(f"'{k}'", val, value_repr=True)

        msg += (Divider.console if print_headers else "")
        return msg
