
import pygame
import sys

from game.game_engine import GameEngine
from ui.agent_manager import AgentManager


# ==========================================
# 1. CONFIGURATION
# ==========================================

pygame.init()

WIDTH = 800
HEIGHT = 960

ROWS = 4
COLS = 4

BOARD_SIZE = 520
CELL_SIZE = BOARD_SIZE // 4

BOARD_X = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = 365

BACKGROUND = (24, 28, 38)
BOARD_COLOR = (35, 42, 56)
LINE_COLOR = (100, 116, 139)

X_COLOR = (56, 189, 248)
O_COLOR = (248, 113, 113)
TEXT_COLOR = (241, 245, 249)
SUBTEXT_COLOR = (148, 163, 184)

BUTTON_COLOR = (51, 65, 85)
BUTTON_HOVER = (71, 85, 105)
ACTIVE_COLOR = (14, 116, 144)
DISABLED_COLOR = (45, 52, 65)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic-Tac-Toe AI")

clock = pygame.time.Clock()

title_font = pygame.font.SysFont("Arial", 36, bold=True)
info_font = pygame.font.SysFont("Arial", 22)
small_font = pygame.font.SysFont("Arial", 17)
mark_font = pygame.font.SysFont("Arial", 90, bold=True)
button_font = pygame.font.SysFont("Arial", 18, bold=True)


# ==========================================
# 2. GAME AND AI INITIALIZATION
# ==========================================

game = GameEngine(board_size=4, win_length=4)

agent_manager = None
# ==========================================
# GAME STATISTICS
# ==========================================

stats = {
    "X": 0,
    "O": 0,
    "DRAW": 0
}

# Đảm bảo mỗi trận chỉ được thống kê một lần
game_counted = False

AGENT_NAMES = [
    "Random",
    "Heuristic",
    "Minimax",
    "Alpha-Beta",
    "MCTS",
    "DQN"
]

selected_agent_index = 0

# PVP: Người vs Người
# AI: Người vs AI
game_mode = "AI"

# Người chơi chọn X hoặc O
human_symbol = 1

# ==========================================
# 3. BUTTON POSITIONS
# ==========================================

# Hàng 1: Dưới chữ "GAME MODE" (y=62), trên chữ "SELECT AI AGENT" (y=120)
mode_pvp_rect = pygame.Rect(235, 74, 155, 34)
mode_ai_rect = pygame.Rect(410, 74, 155, 34)

# Hàng 2: Dưới chữ "SELECT AI AGENT" (y=120), trên chữ "YOUR SYMBOL" (y=180)
# (Khớp với ô tên Agent đang hardcode tại Rect(215, 135, 370, 42) trong draw_menu)
agent_prev_rect = pygame.Rect(155, 140, 50, 34)
agent_next_rect = pygame.Rect(595, 140, 50, 34)

# Hàng 3: Dưới chữ "YOUR SYMBOL" (y=180), trên chữ "YOUR TURN" (y=250)
symbol_x_rect = pygame.Rect(315, 205, 75, 34)
symbol_o_rect = pygame.Rect(410, 205, 75, 34)

# Nút Restart nằm giữa bên dưới bàn cờ (BOARD_Y + BOARD_SIZE = 810)
restart_rect = pygame.Rect(310, 910, 180, 45)


# ==========================================
# 4. DRAW FUNCTIONS
# ==========================================

def draw_text(text, font, color, center):

    surface = font.render(str(text), True, color)

    rect = surface.get_rect(center=center)

    screen.blit(surface, rect)


def draw_button(text, rect, active=False, disabled=False):

    mouse_pos = pygame.mouse.get_pos()

    if disabled:
        color = DISABLED_COLOR
    elif active:
        color = ACTIVE_COLOR
    elif rect.collidepoint(mouse_pos):
        color = BUTTON_HOVER
    else:
        color = BUTTON_COLOR

    pygame.draw.rect(
        screen,
        color,
        rect,
        border_radius=8
    )

    draw_text(
        text,
        button_font,
        TEXT_COLOR,
        rect.center
    )


# ==========================================
# 5. DRAW MENU
# ==========================================

def draw_menu():

    draw_text(
        "TIC-TAC-TOE AI",
        title_font,
        TEXT_COLOR,
        (WIDTH // 2, 35)
    )

    # Chọn chế độ
    draw_text(
        "GAME MODE",
        small_font,
        SUBTEXT_COLOR,
        (WIDTH // 2, 62)
    )

    draw_button(
        "PVP",
        mode_pvp_rect,
        active=(game_mode == "PVP")
    )

    draw_button(
        "PLAYER VS AI",
        mode_ai_rect,
        active=(game_mode == "AI")
    )

    # Chọn AI
    draw_text(
        "SELECT AI AGENT",
        small_font,
        SUBTEXT_COLOR,
        (WIDTH // 2, 120)
    )

    draw_button(
        "<",
        agent_prev_rect,
        disabled=(game_mode == "PVP")
    )

    draw_button(
        AGENT_NAMES[selected_agent_index],
        pygame.Rect(215, 135, 370, 42),
        active=True,
        disabled=(game_mode == "PVP")
    )

    draw_button(
        ">",
        agent_next_rect,
        disabled=(game_mode == "PVP")
    )

    # Chọn quân cờ
    draw_text(
        "YOUR SYMBOL",
        small_font,
        SUBTEXT_COLOR,
        (WIDTH // 2, 190)
    )

    draw_button(
        "X",
        symbol_x_rect,
        active=(human_symbol == 1),
        disabled=(game_mode == "PVP")
    )

    draw_button(
        "O",
        symbol_o_rect,
        active=(human_symbol == -1),
        disabled=(game_mode == "PVP")
    )


# ==========================================
# 6. DRAW GAME STATUS
# ==========================================

def draw_status():

    if game.is_terminal():

        result = game.result()

        if result == "DRAW":
            status = "DRAW!"
            color = TEXT_COLOR

        elif game_mode == "PVP":
            status = f"PLAYER {result} WINS!"
            color = X_COLOR if result == "X" else O_COLOR

        else:

            winner_value = 1 if result == "X" else -1

            if winner_value == human_symbol:
                status = "YOU WIN!"
                color = X_COLOR if result == "X" else O_COLOR
            else:
                status = "AI WINS!"
                color = O_COLOR if result == "O" else X_COLOR

    else:

        current_player = game.state.current_player

        player_symbol = "X" if current_player == 1 else "O"

        color = X_COLOR if current_player == 1 else O_COLOR

        if game_mode == "PVP":

            status = f"CURRENT TURN: {player_symbol}"

        elif current_player == human_symbol:

            status = f"YOUR TURN: {player_symbol}"

        else:

            status = f"AI THINKING... ({player_symbol})"

    draw_text(
        status,
        info_font,
        color,
        (WIDTH // 2, 320)
    )


# ==========================================
# 7. DRAW BOARD
# ==========================================

def draw_board():

    board = game.state.board

    # Nền bàn cờ
    pygame.draw.rect(
        screen,
        BOARD_COLOR,
        (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE),
        border_radius=8
    )

    # Đường kẻ ngang và dọc
    for i in range(1, ROWS):

        position = BOARD_Y + i * CELL_SIZE

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (BOARD_X, position),
            (BOARD_X + BOARD_SIZE, position),
            3
        )

        position = BOARD_X + i * CELL_SIZE

        pygame.draw.line(
            screen,
            LINE_COLOR,
            (position, BOARD_Y),
            (position, BOARD_Y + BOARD_SIZE),
            3
        )

    # Vẽ quân cờ
    for row in range(ROWS):

        for col in range(COLS):

            center_x = BOARD_X + col * CELL_SIZE + CELL_SIZE // 2

            center_y = BOARD_Y + row * CELL_SIZE + CELL_SIZE // 2

            if board[row][col] == 1:

                text = mark_font.render("X", True, X_COLOR)

                screen.blit(
                    text,
                    text.get_rect(center=(center_x, center_y))
                )

            elif board[row][col] == -1:

                text = mark_font.render("O", True, O_COLOR)

                screen.blit(
                    text,
                    text.get_rect(center=(center_x, center_y))
                )


# ==========================================
# 8. DRAW COMPLETE SCREEN
# ==========================================

def draw_screen():

    screen.fill(BACKGROUND)

    draw_menu()

    draw_status()

    draw_board()

    draw_button(
        "RESTART (R)",
        restart_rect
    )

    # Hiển thị thống kê
    draw_statistics()

# ==========================================
# GAME STATISTICS
# ==========================================

def update_statistics():

    global game_counted

    # Không thống kê khi trận đấu chưa kết thúc
    if not game.is_terminal():
        return

    # Tránh ghi nhận kết quả nhiều lần
    if game_counted:
        return

    result = game.result()

    if result == "DRAW":
        stats["DRAW"] += 1

    elif result == "X":
        stats["X"] += 1

    elif result == "O":
        stats["O"] += 1

    game_counted = True

    print("\n========== MATCH RESULT ==========")
    print("Result:", result)
    print("X Wins:", stats["X"])
    print("O Wins:", stats["O"])
    print("Draws:", stats["DRAW"])
    print("Total:", sum(stats.values()))
    print("==================================\n")


def draw_statistics():

    total = sum(stats.values())

    statistics_text = (
        f"X WINS: {stats['X']}     "
        f"O WINS: {stats['O']}     "
        f"DRAWS: {stats['DRAW']}     "
        f"TOTAL: {total}"
    )

    draw_text(
        statistics_text,
        small_font,
        SUBTEXT_COLOR,
        (WIDTH // 2, 895)
    )

# ==========================================
# 9. AI MOVE
# ==========================================

def perform_ai_move():

    if game_mode != "AI":
        return

    if game.is_terminal():
        return

    current_player = game.state.current_player

    # Chỉ gọi AI khi đến lượt AI
    if current_player == human_symbol:
        return

    agent_name = AGENT_NAMES[selected_agent_index]

    try:

        action = agent_manager.get_action(
            game,
            agent_name
        )

        if action is not None:

            game.step(action)

            print(
                f"[AI: {agent_name}] Played: {action}"
            )

    except Exception as error:

        print("AI ERROR:", error)


# ==========================================
# 10. RESET GAME
# ==========================================

def reset_game():

    global game_counted

    game.reset()

    # Cho phép ghi nhận kết quả trận tiếp theo
    game_counted = False

    print("Game restarted!")


# ==========================================
# 11. HANDLE MOUSE CLICK
# ==========================================

def handle_click(position):

    global game_mode
    global selected_agent_index
    global human_symbol

    # Chọn chế độ PVP
    if mode_pvp_rect.collidepoint(position):

        game_mode = "PVP"

        reset_game()

        return

    # Chọn chế độ AI
    if mode_ai_rect.collidepoint(position):

        game_mode = "AI"

        reset_game()

        return

    # Chọn AI trước đó
    if agent_prev_rect.collidepoint(position):

        if game_mode == "AI":

            selected_agent_index = (
                selected_agent_index - 1
            ) % len(AGENT_NAMES)

        return

    # Chọn AI tiếp theo
    if agent_next_rect.collidepoint(position):

        if game_mode == "AI":

            selected_agent_index = (
                selected_agent_index + 1
            ) % len(AGENT_NAMES)

        return

    # Chọn quân X
    if symbol_x_rect.collidepoint(position):

        if game_mode == "AI":

            human_symbol = 1

            reset_game()

        return

    # Chọn quân O
    if symbol_o_rect.collidepoint(position):

        if game_mode == "AI":

            human_symbol = -1

            reset_game()

        return

    # Restart
    if restart_rect.collidepoint(position):

        reset_game()

        return

    # Không cho đánh nếu game kết thúc
    if game.is_terminal():
        return

    # Chỉ nhận click khi đến lượt người chơi
    if game_mode == "AI":

        if game.state.current_player != human_symbol:
            return

    # Kiểm tra click có nằm trong bàn cờ
    mouse_x, mouse_y = position

    if not (
        BOARD_X <= mouse_x < BOARD_X + BOARD_SIZE
        and BOARD_Y <= mouse_y < BOARD_Y + BOARD_SIZE
    ):
        return

    col = (mouse_x - BOARD_X) // CELL_SIZE

    row = (mouse_y - BOARD_Y) // CELL_SIZE

    action = (int(row), int(col))

    # Kiểm tra nước đi hợp lệ
    if action not in game.legal_actions():
        return

    # Đưa nước đi vào Game Engine
    game.step(action)

    print(f"[PLAYER] Played: {action}")


# ==========================================
# 12. MAIN LOOP
# ==========================================

def main():

    global agent_manager

    print("Initializing Agent Manager...")

    agent_manager = AgentManager()

    print("All AI agents are ready!")

    running = True

    while running:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN:

                if event.button == 1:

                    handle_click(event.pos)

            elif event.type == pygame.KEYDOWN:

                if event.key == pygame.K_r:

                    reset_game()

        # Nếu AI được chọn X thì AI sẽ đi trước
        # AI thực hiện nước đi nếu đến lượt
        perform_ai_move()

        # Cập nhật kết quả trận đấu
        update_statistics()

        # Vẽ giao diện
        draw_screen()

        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

    sys.exit()


if __name__ == "__main__":

    main()
