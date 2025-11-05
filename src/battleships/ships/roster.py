#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file roster.py)

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
from dataclasses import dataclass
from typing import Mapping, Optional

# Third-party imports
from pydantic import (
    BaseModel,
    computed_field,
    ConfigDict,
    Field,
    PrivateAttr,
)
from yaml import YAMLError

# Local application imports
from .spec import ShipSpec

from utils import Divider, JustifyText, load_yaml

from src.log import get_logger
log = get_logger(__name__)


# Module-level constants
@dataclass(frozen=True)
class _Defaults:
    """Default `Battleships` ``Roster`` properties.

    Attributes:
        file_path: Default relative path to the configuration file.
    """
    file_path: str = 'battleships/config/rosters.yml'


class Roster(BaseModel):
    """Named set of ship specs loaded from a configuration file.

    Used to build a `Fleet`.

    Expected shape of the configuration file:
        <id>:
            <roster>:
                <ship_type>: { size: <int>, is_cloaded: <bool, optional> }

    Attributes:
        id: Unique ID given to this roster in *rosters.yml*.

        ships: All uninitialised `ShipSpecs`.
    """
    model_config = ConfigDict(frozen=True, validate_default=True)

    id: str
    ships: dict[str, ShipSpec] = Field(default_factory=dict)

    _raw_counts: Optional[Mapping[str, int]] = PrivateAttr(default=None)

    @classmethod
    def load_from_yaml(cls, id_: str, *,
                       filepath: str = _Defaults.file_path) -> 'Roster':
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
            raise KeyError(
                f"Roster ID '{id_!r}' wasn't found at '{filepath!r}'")

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
