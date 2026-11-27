
from game.board import EMPTY, X, O


def get_winning_lines(size=4, win_length=4):
    """
    Tạo tất cả nhóm ô liên tiếp có thể tạo chiến thắng.

    Hỗ trợ:
    - Ngang
    - Dọc
    - Chéo xuống phải
    - Chéo xuống trái
    """

    directions = [
        (0, 1),    # Ngang
        (1, 0),    # Dọc
        (1, 1),    # Chéo xuống phải
        (1, -1)    # Chéo xuống trái
    ]

    lines = []

    for row in range(size):
        for col in range(size):

            for dr, dc in directions:

                end_row = row + (win_length - 1) * dr
                end_col = col + (win_length - 1) * dc

                # Kiểm tra điểm cuối có nằm trong bàn cờ
                if not (
                    0 <= end_row < size
                    and 0 <= end_col < size
                ):
                    continue

                line = []

                for i in range(win_length):

                    r = row + i * dr
                    c = col + i * dc

                    line.append((r, c))

                lines.append(line)

    return lines


def check_winner(board, win_length=4):
    """
    Trả về:
        1  : X thắng
       -1  : O thắng
        0  : Chưa có người thắng
    """

    size = len(board)

    winning_lines = get_winning_lines(
        size,
        win_length
    )

    for line in winning_lines:

        values = [
            board[row][col]
            for row, col in line
        ]

        if values[0] != EMPTY and all(
            value == values[0]
            for value in values
        ):

            return values[0]

    return EMPTY


def check_draw(board, win_length=4):
    """
    Kiểm tra hòa:
    Bàn cờ đầy và không có người thắng.
    """

    if check_winner(board, win_length) != EMPTY:
        return False

    for row in board:
        for cell in row:

            if cell == EMPTY:
                return False

    return True


def is_terminal_board(board, win_length=4):
    """
    Kiểm tra trạng thái bàn cờ đã kết thúc chưa.
    """

    return (
        check_winner(board, win_length) != EMPTY
        or check_draw(board, win_length)
    )
