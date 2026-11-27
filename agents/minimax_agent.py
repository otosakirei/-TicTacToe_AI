
import numpy as np
import time


class MinimaxAgent:
    """
    Minimax Agent for Tic-Tac-Toe 4x4.

    Board representation:
         1 = X
        -1 = O
         0 = Empty

    Action:
        (row, col)

    Experimental metrics:
        - nodes_visited
        - nodes_expanded
        - decision_time
        - nodes_per_second
    """

    def __init__(self, depth=4, name="Minimax Agent"):

        if not isinstance(depth, (int, np.integer)) or isinstance(depth, bool):
            raise TypeError("Depth must be an integer!")

        if depth < 1:
            raise ValueError("Depth must be greater than or equal to 1!")

        self.name = name
        self.depth = int(depth)

        # Search metrics
        self.nodes_visited = 0
        self.nodes_expanded = 0
        self.decision_time = 0.0
        self.nodes_per_second = 0.0

        # Store latest experiment results
        self.last_search_stats = {}

        self.weights = {
            1: 1,
            2: 10,
            3: 100,
            4: 10000
        }

        self.WIN_SCORE = 1000000

    # --------------------------------------------------
    # 1. Generate all winning segments
    # --------------------------------------------------
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

                    end_r = r + (win_length - 1) * dr
                    end_c = c + (win_length - 1) * dc

                    if not (0 <= end_r < board_size):
                        continue

                    if not (0 <= end_c < board_size):
                        continue

                    segment = []

                    for i in range(win_length):
                        segment.append(
                            (r + i * dr, c + i * dc)
                        )

                    segments.append(segment)

        return segments

    # --------------------------------------------------
    # 2. Check winner
    # --------------------------------------------------
    def get_winner(self, board, segments):

        for segment in segments:

            values = [
                board[r][c]
                for r, c in segment
            ]

            if all(value == 1 for value in values):
                return 1

            if all(value == -1 for value in values):
                return -1

        return 0

    # --------------------------------------------------
    # 3. Check whether board is full
    # --------------------------------------------------
    def is_board_full(self, board):

        return not np.any(board == 0)

    # --------------------------------------------------
    # 4. Evaluate board
    # --------------------------------------------------
    def evaluate_board(self, board, player, segments):

        winner = self.get_winner(board, segments)

        if winner == player:
            return self.WIN_SCORE

        if winner == -player:
            return -self.WIN_SCORE

        if self.is_board_full(board):
            return 0

        score = 0

        for segment in segments:

            values = [
                board[r][c]
                for r, c in segment
            ]

            player_count = values.count(player)
            opponent_count = values.count(-player)

            # Ignore segments occupied by both players
            if player_count > 0 and opponent_count > 0:
                continue

            if player_count > 0:
                score += self.weights[player_count]

            elif opponent_count > 0:
                score -= self.weights[opponent_count]

        return score

    # --------------------------------------------------
    # 5. Order actions: center first
    # --------------------------------------------------
    def order_actions(self, actions, board_size):

        center = (board_size - 1) / 2

        return sorted(
            actions,
            key=lambda action: (
                (action[0] - center) ** 2
                + (action[1] - center) ** 2
            )
        )

    # --------------------------------------------------
    # 6. Minimax algorithm
    # --------------------------------------------------
    def minimax(
        self,
        board,
        depth,
        maximizing,
        player,
        segments,
        board_size
    ):

        # Count visited search nodes
        self.nodes_visited += 1
        self.nodes_expanded += 1

        winner = self.get_winner(board, segments)

        # Terminal states
        if winner == player:
            return self.WIN_SCORE + depth

        if winner == -player:
            return -self.WIN_SCORE - depth

        if self.is_board_full(board):
            return 0

        if depth == 0:
            return self.evaluate_board(
                board, player, segments
            )

        # Find legal actions
        actions = [
            (r, c)
            for r in range(board_size)
            for c in range(board_size)
            if board[r][c] == 0
        ]

        actions = self.order_actions(actions, board_size)

        if maximizing:

            best_score = float("-inf")

            for r, c in actions:

                board[r][c] = player

                score = self.minimax(
                    board,
                    depth - 1,
                    False,
                    player,
                    segments,
                    board_size
                )

                board[r][c] = 0

                best_score = max(best_score, score)

            return best_score

        else:

            best_score = float("inf")

            for r, c in actions:

                board[r][c] = -player

                score = self.minimax(
                    board,
                    depth - 1,
                    True,
                    player,
                    segments,
                    board_size
                )

                board[r][c] = 0

                best_score = min(best_score, score)

            return best_score

    # --------------------------------------------------
    # 7. Choose best action
    # --------------------------------------------------
    def choose_action(self, game):

        start_time = time.perf_counter()

        # Reset metrics for each decision
        self.nodes_visited = 0
        self.nodes_expanded = 0

        state = game.get_state()

        board = np.array(state.board, dtype=int).copy()

        player = int(state.current_player)

        board_size = game.board_size
        win_length = game.win_length

        actions = game.legal_actions()

        if not actions:

            self.decision_time = time.perf_counter() - start_time
            self.nodes_per_second = 0.0

            self.last_search_stats = self.get_search_stats()

            return None

        segments = self.get_segments(
            board_size,
            win_length
        )

        actions = self.order_actions(
            actions,
            board_size
        )

        best_action = None
        best_score = float("-inf")

        for r, c in actions:

            board[r][c] = player

            score = self.minimax(
                board,
                self.depth - 1,
                False,
                player,
                segments,
                board_size
            )

            board[r][c] = 0

            if score > best_score:
                best_score = score
                best_action = (r, c)

        # Record decision time
        self.decision_time = time.perf_counter() - start_time

        # Calculate search speed
        if self.decision_time > 0:
            self.nodes_per_second = (
                self.nodes_visited / self.decision_time
            )
        else:
            self.nodes_per_second = 0.0

        # Save latest experiment metrics
        self.last_search_stats = self.get_search_stats()

        return best_action

    # --------------------------------------------------
    # 8. Get search statistics
    # --------------------------------------------------
    def get_search_stats(self):

        return {
            "agent": self.name,
            "algorithm": "Minimax",
            "depth": self.depth,
            "nodes_visited": self.nodes_visited,
            "nodes_expanded": self.nodes_expanded,
            "decision_time": self.decision_time,
            "nodes_per_second": self.nodes_per_second
        }

    # --------------------------------------------------
    # 9. String representation
    # --------------------------------------------------
    def __str__(self):

        return self.name
