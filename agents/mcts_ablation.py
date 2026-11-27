
import random
import math
from copy import deepcopy

from agents.mcts_agent import MCTSAgent, MCTSNode


class MCTSNoExpansionAgent(MCTSAgent):
    """
    Ablation: Loại bỏ bước Expansion.

    Mỗi simulation bắt đầu từ root và rollout
    trực tiếp đến trạng thái kết thúc.
    """

    def search(self, board, player):

        root = MCTSNode(
            board=deepcopy(board),
            player_to_move=player,
            untried_actions=self.get_legal_actions(board)
        )

        self.nodes_created = 1
        self.nodes_visited = 1

        action_stats = {
            action: {"visits": 0, "wins": 0.0}
            for action in root.untried_actions
        }

        for action in root.untried_actions:

            for _ in range(self.simulations):

                rollout_board = deepcopy(board)

                r, c = action
                rollout_board[r][c] = player

                winner = self.rollout(
                    rollout_board,
                    -player,
                    self.segments
                )

                stats = action_stats[action]
                stats["visits"] += 1

                if winner == 0:
                    stats["wins"] += 0.5
                elif winner == player:
                    stats["wins"] += 1

                self.simulations_completed += 1

        if not action_stats:
            return None

        best_action = max(
            action_stats,
            key=lambda action: (
                action_stats[action]["wins"]
                / action_stats[action]["visits"]
            )
        )

        return best_action
