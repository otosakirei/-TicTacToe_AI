
import math
import random
import time

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class MCTSNode:

    board: list
    player_to_move: int

    parent: Optional[object] = None
    action: Optional[tuple] = None

    untried_actions: list = field(default_factory=list)
    children: list = field(default_factory=list)

    visits: int = 0
    wins: float = 0.0

    # Player who made the move leading to this node
    player_just_moved: Optional[int] = None

    def uct_value(self, exploration=math.sqrt(2)):

        if self.visits == 0:
            return float("inf")

        if self.parent is None:
            return 0

        exploitation = self.wins / self.visits

        exploration_term = exploration * math.sqrt(
            math.log(max(1, self.parent.visits))
            / self.visits
        )

        return exploitation + exploration_term

    def select_child(self, exploration=math.sqrt(2)):

        if not self.children:
            return None

        return max(
            self.children,
            key=lambda child: child.uct_value(exploration)
        )


class MCTSAgent:

    def __init__(
        self,
        simulations=1000,
        exploration=math.sqrt(2),
        seed=None,
        name="MCTS Agent"
    ):

        if (
            not isinstance(simulations, int)
            or isinstance(simulations, bool)
        ):
            raise TypeError("Simulations must be an integer!")

        if simulations < 1:
            raise ValueError("Simulations must be >= 1!")

        if not isinstance(exploration, (int, float)):
            raise TypeError("Exploration must be a number!")

        if exploration < 0:
            raise ValueError("Exploration must be >= 0!")

        self.name = name
        self.simulations = simulations
        self.exploration = float(exploration)
        self.seed = seed

        self.rng = random.Random(seed)

        # -----------------------------------------
        # Experimental metrics
        # -----------------------------------------

        self.nodes_visited = 0
        self.nodes_created = 0
        self.tree_nodes_visited = 0

        self.simulations_completed = 0
        self.rollout_steps = 0

        self.decision_time = 0.0
        self.simulations_per_second = 0.0

        self.last_search_stats = {}

        # Game information
        self.board_size = None
        self.win_length = None
        self.segments = None

    # -----------------------------------------
    # 1. Generate legal actions
    # -----------------------------------------
    def get_legal_actions(self, board):

        actions = []

        for r in range(len(board)):
            for c in range(len(board[r])):

                if board[r][c] == 0:
                    actions.append((r, c))

        return actions

    # -----------------------------------------
    # 2. Generate winning segments
    # -----------------------------------------
    def get_segments(self, board_size, win_length):

        segments = []

        directions = [
            (0, 1),
            (1, 0),
            (1, 1),
            (1, -1)
        ]

        for r in range(board_size):
            for c in range(board_size):

                for dr, dc in directions:

                    segment = []

                    for i in range(win_length):

                        nr = r + i * dr
                        nc = c + i * dc

                        if not (
                            0 <= nr < board_size
                            and 0 <= nc < board_size
                        ):
                            break

                        segment.append((nr, nc))

                    if len(segment) == win_length:
                        segments.append(segment)

        return segments

    # -----------------------------------------
    # 3. Check winner
    # -----------------------------------------
    def get_winner(self, board, segments):

        for segment in segments:

            values = [
                board[r][c]
                for r, c in segment
            ]

            if values[0] != 0 and all(
                value == values[0]
                for value in values
            ):
                return values[0]

        return 0

    # -----------------------------------------
    # 4. Check terminal state
    # -----------------------------------------
    def is_terminal(self, board, segments):

        winner = self.get_winner(board, segments)

        if winner != 0:
            return True

        return not self.get_legal_actions(board)

    # -----------------------------------------
    # 5. Random rollout
    # -----------------------------------------
    def rollout(self, board, player, segments):

        while True:

            winner = self.get_winner(board, segments)

            if winner != 0:
                return winner

            actions = self.get_legal_actions(board)

            if not actions:
                return 0

            action = self.rng.choice(actions)

            r, c = action

            board[r][c] = player

            # Count rollout moves
            self.rollout_steps += 1

            player = -player

    # -----------------------------------------
    # 6. Backpropagation
    # -----------------------------------------
    def backpropagate(self, node, winner):

        while node is not None:

            node.visits += 1

            if winner == 0:
                node.wins += 0.5

            elif winner == node.player_just_moved:
                node.wins += 1

            node = node.parent

    # -----------------------------------------
    # 7. Selection
    # -----------------------------------------
    def selection(self, node):

        while True:

            # Count each tree node visited during Selection
            self.tree_nodes_visited += 1

            if self.is_terminal(node.board, self.segments):
                break

            # Stop Selection if unexplored actions remain
            if node.untried_actions:
                break

            if not node.children:
                break

            node = node.select_child(self.exploration)

            if node is None:
                break

        return node

    # -----------------------------------------
    # 8. Expansion
    # -----------------------------------------
    def expansion(self, node):

        if not node.untried_actions:
            return node

        # Select a random unexplored action
        action = self.rng.choice(node.untried_actions)

        node.untried_actions.remove(action)

        r, c = action

        # Create new board
        new_board = deepcopy(node.board)

        player = node.player_to_move

        new_board[r][c] = player

        # Next player
        next_player = -player

        # Create child node
        child = MCTSNode(
            board=new_board,
            player_to_move=next_player,
            parent=node,
            action=action,
            player_just_moved=player,
            untried_actions=self.get_legal_actions(new_board)
        )

        node.children.append(child)

        # Count newly created node
        self.nodes_created += 1

        # Keep old metric compatible
        self.nodes_visited = self.nodes_created

        return child

    # -----------------------------------------
    # 9. Main MCTS Search
    # -----------------------------------------
    def search(self, board, player):

        root = MCTSNode(
            board=deepcopy(board),
            player_to_move=player,
            untried_actions=self.get_legal_actions(board)
        )

        # Count root node
        self.nodes_created = 1
        self.nodes_visited = 1

        for _ in range(self.simulations):

            # 1. Selection
            node = self.selection(root)

            # 2. Expansion
            if not self.is_terminal(node.board, self.segments):
                node = self.expansion(node)

            # 3. Simulation
            rollout_board = deepcopy(node.board)

            winner = self.rollout(
                rollout_board,
                node.player_to_move,
                self.segments
            )

            # 4. Backpropagation
            self.backpropagate(node, winner)

            # Count completed simulation
            self.simulations_completed += 1

        if not root.children:
            return None

        # Choose child with the highest visit count
        best_child = max(
            root.children,
            key=lambda child: child.visits
        )

        return best_child.action

    # -----------------------------------------
    # 10. Choose action
    # -----------------------------------------
    def choose_action(self, game):

        start_time = time.perf_counter()

        # Reset metrics for each decision
        self.nodes_visited = 0
        self.nodes_created = 0
        self.tree_nodes_visited = 0

        self.simulations_completed = 0
        self.rollout_steps = 0

        self.decision_time = 0.0
        self.simulations_per_second = 0.0

        self.last_search_stats = {}

        state = game.get_state()

        board = [
            list(row)
            for row in state.board
        ]

        player = int(state.current_player)

        board_size = game.board_size
        win_length = game.win_length

        self.board_size = board_size
        self.win_length = win_length

        self.segments = self.get_segments(
            board_size,
            win_length
        )

        actions = game.legal_actions()

        if not actions:

            self.decision_time = (
                time.perf_counter() - start_time
            )

            self.last_search_stats = self.get_search_stats()

            return None

        # If only one legal action remains
        if len(actions) == 1:

            action = actions[0]

        else:

            action = self.search(board, player)

        # Record decision time
        self.decision_time = (
            time.perf_counter() - start_time
        )

        # Calculate simulation speed
        if self.decision_time > 0:
            self.simulations_per_second = (
                self.simulations_completed / self.decision_time
            )
        else:
            self.simulations_per_second = 0.0

        # Save latest experiment metrics
        self.last_search_stats = self.get_search_stats()

        return action

    # -----------------------------------------
    # 11. Get search statistics
    # -----------------------------------------
    def get_search_stats(self):

        return {
            "agent": self.name,
            "algorithm": "MCTS",
            "simulations": self.simulations,
            "simulations_completed": self.simulations_completed,
            "exploration": self.exploration,
            "seed": self.seed,
            "nodes_visited": self.nodes_visited,
            "nodes_created": self.nodes_created,
            "tree_nodes_visited": self.tree_nodes_visited,
            "rollout_steps": self.rollout_steps,
            "decision_time": self.decision_time,
            "simulations_per_second": self.simulations_per_second
        }

    # -----------------------------------------
    # 12. String representation
    # -----------------------------------------
    def __str__(self):

        return self.name
