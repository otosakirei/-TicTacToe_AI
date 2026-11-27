
import numpy as np
import time

from agents.minimax_agent import MinimaxAgent


class AlphaBetaAgent(MinimaxAgent):
    """
    Alpha-Beta Pruning Agent for Tic-Tac-Toe 4x4.

    Inherits board evaluation and helper methods from MinimaxAgent.

    Experimental metrics:
        - nodes_visited
        - nodes_expanded
        - pruned_branches
        - cutoffs
        - actions_considered
        - decision_time
        - nodes_per_second
    """

    def __init__(self, depth=4, name="Alpha-Beta Agent"):

        # Initialize inherited attributes and validate depth
        super().__init__(depth=depth, name=name)

        # Alpha-Beta specific metrics
        self.pruned_branches = 0
        self.cutoffs = 0
        self.actions_considered = 0

    # --------------------------------------------------
    # 1. Minimax with Alpha-Beta Pruning
    # --------------------------------------------------
    def minimax(
        self,
        board,
        depth,
        maximizing,
        player,
        segments,
        board_size,
        alpha,
        beta
    ):

        # Count visited search nodes
        self.nodes_visited += 1
        self.nodes_expanded += 1

        winner = self.get_winner(board, segments)

        # Check terminal states
        if winner == player:
            return self.WIN_SCORE + depth

        if winner == -player:
            return -self.WIN_SCORE - depth

        if self.is_board_full(board):
            return 0

        # Stop searching when reaching depth limit
        if depth <= 0:
            return self.evaluate_board(
                board, player, segments
            )

        # Generate legal actions
        actions = [
            (r, c)
            for r in range(board_size)
            for c in range(board_size)
            if board[r][c] == 0
        ]

        actions = self.order_actions(actions, board_size)

        if maximizing:

            best_score = float("-inf")

            for index, (r, c) in enumerate(actions):

                self.actions_considered += 1

                board[r][c] = player

                score = self.minimax(
                    board,
                    depth - 1,
                    False,
                    player,
                    segments,
                    board_size,
                    alpha,
                    beta
                )

                board[r][c] = 0

                best_score = max(best_score, score)
                alpha = max(alpha, best_score)

                # Alpha-Beta pruning
                if beta <= alpha:

                    self.cutoffs += 1

                    # Count unexplored sibling branches
                    self.pruned_branches += (
                        len(actions) - index - 1
                    )

                    break

            return best_score

        else:

            best_score = float("inf")

            for index, (r, c) in enumerate(actions):

                self.actions_considered += 1

                board[r][c] = -player

                score = self.minimax(
                    board,
                    depth - 1,
                    True,
                    player,
                    segments,
                    board_size,
                    alpha,
                    beta
                )

                board[r][c] = 0

                best_score = min(best_score, score)
                beta = min(beta, best_score)

                # Alpha-Beta pruning
                if beta <= alpha:

                    self.cutoffs += 1

                    # Count unexplored sibling branches
                    self.pruned_branches += (
                        len(actions) - index - 1
                    )

                    break

            return best_score

    # --------------------------------------------------
    # 2. Choose best action
    # --------------------------------------------------
    def choose_action(self, game):

        start_time = time.perf_counter()

        # Reset metrics for each decision
        self.nodes_visited = 0
        self.nodes_expanded = 0
        self.pruned_branches = 0
        self.cutoffs = 0
        self.actions_considered = 0

        state = game.get_state()

        board = np.array(
            state.board, dtype=int
        ).copy()

        player = int(state.current_player)

        board_size = game.board_size
        win_length = game.win_length

        actions = game.legal_actions()

        if not actions:

            self.decision_time = (
                time.perf_counter() - start_time
            )

            self.nodes_per_second = 0.0
            self.last_search_stats = self.get_search_stats()

            return None

        segments = self.get_segments(
            board_size,
            win_length
        )

        actions = self.order_actions(
            actions, board_size
        )

        best_action = None
        best_score = float("-inf")

        alpha = float("-inf")
        beta = float("inf")

        for r, c in actions:

            self.actions_considered += 1

            board[r][c] = player

            score = self.minimax(
                board,
                self.depth - 1,
                False,
                player,
                segments,
                board_size,
                alpha,
                beta
            )

            board[r][c] = 0

            if score > best_score:
                best_score = score
                best_action = (r, c)

            alpha = max(alpha, best_score)

        # Calculate decision time
        self.decision_time = (
            time.perf_counter() - start_time
        )

        # Calculate search speed
        if self.decision_time > 0:
            self.nodes_per_second = (
                self.nodes_visited / self.decision_time
            )
        else:
            self.nodes_per_second = 0.0

        # Save latest experiment results
        self.last_search_stats = self.get_search_stats()

        return best_action

    # --------------------------------------------------
    # 3. Get Alpha-Beta search statistics
    # --------------------------------------------------
    def get_search_stats(self):

        stats = super().get_search_stats()

        stats.update({
            "algorithm": "Alpha-Beta",
            "pruned_branches": self.pruned_branches,
            "cutoffs": self.cutoffs,
            "actions_considered": self.actions_considered
        })

        total_branches = (
            self.actions_considered + self.pruned_branches
        )

        if total_branches > 0:
            pruning_rate = (
                self.pruned_branches / total_branches
            ) * 100
        else:
            pruning_rate = 0.0

        stats["pruning_rate"] = pruning_rate

        return stats

    # --------------------------------------------------
    # 4. String representation
    # --------------------------------------------------
    def __str__(self):

        return self.name
