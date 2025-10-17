#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file log.py)

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
        src/log.py
    Author
        Cameron Aidan McEleney < c.mceleney.1@research.gla.ac.uk >
    Created
        17 Oct 2025
    IDE
        PyCharm
        
.. _Google Python Style Guide:
   https://google.github.io/styleguide/pyguide.html
"""

from __future__ import annotations

# Standard library imports
import logging
# Third-party imports

# Local application imports

# Module-level constants

__all__ = ['']


def get_logger(name: str = 'custom_logger') -> logging.Logger:
    """"""
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt=f"{'-'*32}\n"
                f"[%(asctime)s] (%(levelname)s)\n"
                f"%(message)s\n"
                f"{'-'*32}\n",
            datefmt="%H:%M:%S")

        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger
