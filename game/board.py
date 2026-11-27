
BOARD_SIZE = 4

EMPTY = 0
X = 1
O = -1


def create_empty_board(size=BOARD_SIZE):
    """
    Tạo bàn cờ mới.
    0: Ô trống
    1: X
   -1: O
    """
    return [
        [EMPTY for _ in range(size)]
        for _ in range(size)
    ]


def get_legal_actions(board):
    """
    Trả về danh sách các ô còn trống.

    Mỗi hành động có dạng:
    (row, col)
    """
    actions = []

    for row in range(len(board)):
        for col in range(len(board[row])):

            if board[row][col] == EMPTY:
                actions.append((row, col))

    return actions


def is_valid_position(board, row, col):
    """
    Kiểm tra tọa độ có nằm trong bàn cờ không.
    """
    size = len(board)

    return (
        isinstance(row, int)
        and not isinstance(row, bool)
        and isinstance(col, int)
        and not isinstance(col, bool)
        and 0 <= row < size
        and 0 <= col < size
    )


def copy_board(board):
    """
    Tạo bản sao độc lập của bàn cờ.
    """
    return [row[:] for row in board]


def render_board(board):
    """
    Chuyển bàn cờ thành chuỗi để hiển thị.
    """

    symbols = {
        EMPTY: " ",
        X: "X",
        O: "O"
    }

    size = len(board)

    header = "    " + "   ".join(
        str(col) for col in range(size)
    )

    separator = "  +" + "---+" * size

    lines = [header, separator]

    for row in range(size):

        cells = [
            symbols[board[row][col]]
            for col in range(size)
        ]

        line = f"{row} | " + " | ".join(cells) + " |"

        lines.append(line)
        lines.append(separator)

    return "\n".join(lines)
