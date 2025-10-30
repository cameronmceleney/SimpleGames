#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file messages.py)

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
        src/battleships/player.py
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

# Third-party imports

# Local application imports

# Module-level constants


class _PlayerMessages(dict):
    """Messages to display to the player."""
    make_guess = "Enter the co-ordinates of your next shot: "


PlayerMessages = _PlayerMessages()
