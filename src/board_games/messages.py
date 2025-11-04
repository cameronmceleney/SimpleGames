#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

# Standard library imports
from enum import StrEnum

__all__ = ['Messages']


class Messages(StrEnum):
    """Text that is displayed in the console.
    """
    END_TURN = ">>> Press 'Enter' to end turn..."
    AI_END_TURN = "Turn complete."
    WINNER = 'Congratulations on winning!'
    KEEP_PLAYING = ' No winner (no active players).'
    ELIMINATED = "This player has been eliminated!"
