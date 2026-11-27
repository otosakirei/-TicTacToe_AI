
from game.board import (
    create_empty_board,
    get_legal_actions,
    is_valid_position,
    render_board,
    X,
    O,
    EMPTY
)

from game.rules import (
    check_winner,
    check_draw
)

from game.state import GameState


class GameEngine:

    def __init__(self, board_size=4, win_length=4):

        if board_size < 1:
            raise ValueError("Kich thuoc ban co phai >= 1")

        if not 1 <= win_length <= board_size:
            raise ValueError("win_length khong hop le")

        self.board_size = board_size
        self.win_length = win_length

        self.reset()


    # =====================================
    # 1. RESET GAME
    # =====================================

    def reset(self):
        """
        Khởi tạo một ván game mới.
        X luôn được đi trước.
        """

        self.state = GameState(
            board=create_empty_board(self.board_size),
            current_player=X,
            move_count=0
        )

        self.history = []

        return self.get_state()


    # =====================================
    # 2. GET LEGAL ACTIONS
    # =====================================

    def legal_actions(self):
        """
        Trả về tất cả các ô còn trống.

        Mỗi action có dạng (row, col).
        """

        if self.is_terminal():
            return []

        return get_legal_actions(
            self.state.board
        )


    # =====================================
    # 3. CHECK RESULT
    # =====================================

    def result(self):
        """
        Kết quả:
            'X'    : X thắng
            'O'    : O thắng
            'DRAW' : Hòa
            None   : Chưa kết thúc
        """

        winner = check_winner(
            self.state.board,
            self.win_length
        )

        if winner == X:
            return "X"

        if winner == O:
            return "O"

        if check_draw(
            self.state.board,
            self.win_length
        ):
            return "DRAW"

        return None


    # =====================================
    # 4. CHECK TERMINAL
    # =====================================

    def is_terminal(self):
        """
        Kiểm tra trò chơi đã kết thúc chưa.
        """

        return self.result() is not None


    # =====================================
    # 5. STEP
    # =====================================

    def step(self, action):
        """
        Thực hiện một nước đi.

        action = (row, col)

        Trả về:
            Kết quả hiện tại nếu game kết thúc.
            None nếu game chưa kết thúc.

        Ném ValueError nếu nước đi không hợp lệ.
        """

        if self.is_terminal():
            raise ValueError(
                "Tro choi da ket thuc!"
            )

        # Kiểm tra định dạng action
        if not isinstance(action, (tuple, list)):
            raise ValueError(
                "Action phai la tuple hoac list!"
            )

        if len(action) != 2:
            raise ValueError(
                "Action phai co dang (row, col)!"
            )

        row, col = action

        # Kiểm tra tọa độ
        if not is_valid_position(
            self.state.board,
            row,
            col
        ):
            raise ValueError(
                "Toa do nam ngoai ban co!"
            )

        # Kiểm tra ô đã được đánh chưa
        if self.state.board[row][col] != EMPTY:
            raise ValueError(
                "O nay da duoc danh!"
            )

        # Lưu lịch sử trước khi thay đổi trạng thái
        previous_player = self.state.current_player

        self.history.append(
            (row, col, previous_player)
        )

        # Đánh dấu quân của người chơi hiện tại
        self.state.board[row][col] = previous_player

        # Tăng số nước đã đi
        self.state.move_count += 1

        # Chuyển lượt
        self.state.current_player = (
            -previous_player
        )

        return self.result()


    # =====================================
    # 6. RENDER
    # =====================================

    def render(self):
        """
        Hiển thị bàn cờ.
        """

        return render_board(
            self.state.board
        )


    # =====================================
    # 7. CLONE
    # =====================================

    def clone(self):
        """
        Sao chép toàn bộ trạng thái game.

        Không ảnh hưởng đến game gốc.
        """

        new_game = GameEngine(
            board_size=self.board_size,
            win_length=self.win_length
        )

        new_game.state = self.state.copy()

        new_game.history = self.history.copy()

        return new_game


    # =====================================
    # 8. UNDO
    # =====================================

    def undo(self):
        """
        Hoàn tác nước đi gần nhất.

        Trả về:
            True  : Hoàn tác thành công.
            False : Không có nước đi để hoàn tác.
        """

        if not self.history:
            return False

        row, col, previous_player = (
            self.history.pop()
        )

        # Xóa quân đã đánh
        self.state.board[row][col] = EMPTY

        # Khôi phục người chơi
        self.state.current_player = previous_player

        # Giảm số nước đã đi
        self.state.move_count -= 1

        return True


    # =====================================
    # 9. GET STATE
    # =====================================

    def get_state(self):
        """
        Trả về bản sao trạng thái hiện tại.
        """

        return self.state.copy()


    # =====================================
    # 10. GET CURRENT PLAYER
    # =====================================

    def get_current_player(self):

        if self.state.current_player == X:
            return "X"

        return "O"
