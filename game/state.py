
from dataclasses import dataclass, field

from game.board import create_empty_board, X


@dataclass
class GameState:

    board: list = field(
        default_factory=create_empty_board
    )

    current_player: int = X

    move_count: int = 0

    def copy(self):
        """
        Tạo bản sao trạng thái game.
        """

        return GameState(
            board=[
                row[:] for row in self.board
            ],
            current_player=self.current_player,
            move_count=self.move_count
        )
