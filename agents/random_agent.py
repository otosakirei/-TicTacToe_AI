
import random


class RandomAgent:
    """
    AI chọn nước đi ngẫu nhiên.
    """

    def __init__(self, name="Random Agent"):
        self.name = name

    def choose_action(self, game):
        """
        Chọn ngẫu nhiên một nước đi hợp lệ.

        Parameters:
            game: Đối tượng GameEngine

        Returns:
            (row, col): Vị trí được chọn.
        """

        legal_actions = game.legal_actions()

        if not legal_actions:
            return None

        return random.choice(legal_actions)
