
class HeuristicAgent:
    """
    AI sử dụng phương pháp Heuristic.
    X = 1, O = -1, EMPTY = 0.
    """

    WIN_SCORE = 100000
    BLOCK_SCORE = 50000

    def __init__(self, name="Heuristic Agent"):
        self.name = name

    def get_segments(self, board_size, win_length):
        segments = []
        directions = [
            (0, 1), (1, 0), (1, 1), (1, -1)
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

                    segments.append([
                        (r + i * dr, c + i * dc)
                        for i in range(win_length)
                    ])

        return segments

    def evaluate_board(self, board, player, segments):
        opponent = -player
        score = 0

        weights = {
            1: 2,
            2: 15,
            3: 1000,
            4: self.WIN_SCORE
        }

        for segment in segments:
            values = [board[r][c] for r, c in segment]

            own_count = values.count(player)
            opponent_count = values.count(opponent)

            if opponent_count == 0 and own_count > 0:
                score += weights.get(own_count, 0)

            elif own_count == 0 and opponent_count > 0:
                score -= weights.get(opponent_count, 0) * 1.1

        return score

    def is_winning_move(self, board, action, player, segments):
        r, c = action
        board[r][c] = player

        won = any(
            all(board[x][y] == player for x, y in segment)
            for segment in segments
        )

        board[r][c] = 0
        return won

    def choose_action(self, game):
        state = game.get_state()
        board = [list(row) for row in state.board]

        player = state.current_player
        opponent = -player

        legal_actions = game.legal_actions()

        if not legal_actions:
            return None

        segments = self.get_segments(
            game.board_size,
            game.win_length
        )

        # Ưu tiên nước đi giúp AI thắng ngay
        for action in legal_actions:
            if self.is_winning_move(
                board, action, player, segments
            ):
                return action

        # Ưu tiên chặn đối thủ thắng ngay
        for action in legal_actions:
            if self.is_winning_move(
                board, action, opponent, segments
            ):
                return action

        best_action = None
        best_score = float("-inf")

        center = (game.board_size - 1) / 2

        for r, c in legal_actions:
            board[r][c] = player

            score = self.evaluate_board(
                board, player, segments
            )

            # Ưu tiên các ô gần trung tâm
            distance = abs(r - center) + abs(c - center)
            score += max(0, 20 - distance * 5)

            board[r][c] = 0

            if score > best_score:
                best_score = score
                best_action = (r, c)

        return best_action
