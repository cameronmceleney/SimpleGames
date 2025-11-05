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

from .player import AIPlayer, HumanPlayer
from src.log import get_logger

if TYPE_CHECKING:
    from board_games.coordinate import CoordLike
log = get_logger(__name__)


class Game(BaseGame):
    """"""

    def __init__(self, board_size: CoordLike = (10, 10), *,
                 players_names: Optional[list[str]] = None,
                 autoplay: bool = False):
        super().__init__(emitter=None)
        self.board = Board(*board_size)

        if players_names:
            self.add_players(*players_names)

        if autoplay:
            self.board.show()

    @property
    def remaining_players(
            self,
            category: Literal['human', 'ai', 'both'] = 'both'
    ):
        # TODO: Consider if method is problematic; `remaining_players` in ABC doesn't have `category` arg.
        counts = Counter()
        for p in self.players:
            if isinstance(p, HumanPlayer) and p.is_still_playing:
                counts['human'] += 1
            elif isinstance(p, AIPlayer) and p.is_still_playing:
                counts['ai'] += 1

        return counts.total() if category == 'both' else counts[category]

    def _create_human_player(
            self,
            name: str,
            config_file: Optional[str] = None,
            board: Optional[Board] = None,
    ) -> 'HumanPlayer':
        """Create and fully initialise a human player."""
        player = HumanPlayer(
            name=name.capitalize(),
            id=len(self.players),
            board=board or Board(*self.board.dims),
        )
        log.debug(player)

        # TODO: Improve `config_file or None` syntax; might need to refactor method
        player.apply_placements(config_file)
        return player

    def _create_ai_player(
            self, name: str = "CPU",
            suffix: str = '', *,
            config_file: Optional[str] = None
    ) -> AIPlayer:
        """Small helper to add AI players to a game.
        """
        player = AIPlayer(
            name=f'{name}_{suffix}' if suffix else name,
            id=len(self.players),
            board=Board(*self.board.dims),
        )

        player.apply_placements(config_file)
        return player

    def add_players(self, *names: str, num_ai: int = 0) -> None:
        """Add human players by name and optionally AI players."""
        """Add human players by name and optionally AI players."""
        # TODO: Consider if this method conflicts with signature of `BaseGame.add_players` in problematic ways.
        new_players = [self._create_human_player(n) for n in names]
        new_players += [self._create_ai_player(suffix=str(i)) for i in range(num_ai)]
        super().add_players(*new_players)


def test_battleships() -> None:
    bs = Game(board_size=(5, 5), autoplay=False)
    bs.add_players("cameron", num_ai=1)
    # print(f"Players\n{bs.players}")
    bs.play()


if __name__ == '__main__':
    test_battleships()
