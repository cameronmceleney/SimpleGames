#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""(One liner introducing this file game.py)

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
        src/battleships/game.py
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
from typing import Literal, Optional, TYPE_CHECKING

# Third-party imports


# Local application imports
from battleships.board import Board
from board_games import BaseGame

from .player import DEFAULT_PLAYER, AIPlayer, HumanPlayer
from src.log import get_logger

if TYPE_CHECKING:
    from board_games.coordinate import coordinate_type
log = get_logger(__name__)


class Game(BaseGame):
    """"""

    def __init__(self, board_size: coordinate_type = (10, 10), *,
                 players_names: Optional[list[str]] = None,
                 autoplay: bool = False):
        super().__init__(emitter=None)
        self.board = Board(*board_size)

        if players_names:
            self.add_players(*players_names)

        if autoplay:
            self.board.show()

    def _create_human_player(
            self,
            name: str,
            config_file: str | None = None,
            board: Optional[Board] = None,
    ) -> 'HumanPlayer':
        """Create and fully initialise a human player."""
        player = HumanPlayer(
            name=name.capitalize(),
            id=len(self.players),
            board=board or Board(height=self.board.height, width=self.board.width),

        )
        log.debug(player)

        player.apply_positions(config_file or DEFAULT_PLAYER)
        return player

    def _create_ai_player(self, name: str = "CPU",
                          suffix: str = '') -> AIPlayer:
        """Small helper to add AI players to a game.
        """
        player = AIPlayer(
            name=f'{name}_{suffix}' if suffix else name,
            id=len(self.players),
            board=Board(height=self.board.height, width=self.board.width),
        )

        player.apply_positions(DEFAULT_PLAYER)
        return player

    def add_players(self, *names: str, num_ai: int = 0) -> None:
        """Add human players by name and optionally AI players."""
        new_players = [self._create_human_player(n) for n in names]
        new_players += [self._create_ai_player(suffix=str(i)) for i in range(num_ai)]
        super().add_players(*new_players)

    def remaining_players(
            self, category: Literal['human', 'ai', 'both'] = 'both') -> int:
        counts = Counter()
        for p in self.players:
            if isinstance(p, HumanPlayer) and p.is_still_playing:
                counts['human'] += 1
            elif isinstance(p, AIPlayer) and p.is_still_playing:
                counts['ai'] += 1

        return counts.total() if category == 'both' else counts[category]


def test_battleships() -> None:
    bs = Game(board_size=(5, 5), autoplay=False)
    bs.add_players("cameron", num_ai=1)
    # print(f"Players\n{bs.players}")
    bs.play()


if __name__ == '__main__':
    test_battleships()
