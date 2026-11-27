
import pytest

from game.game_engine import GameEngine
from game.board import EMPTY, X, O


def test_initial_game():

    game = GameEngine()

    assert game.state.current_player == X
    assert game.state.move_count == 0

    assert len(game.legal_actions()) == 16

    assert game.result() is None


def test_valid_moves():

    game = GameEngine()

    game.step((0, 0))

    assert game.state.board[0][0] == X
    assert game.state.current_player == O

    game.step((1, 1))

    assert game.state.board[1][1] == O
    assert game.state.current_player == X


def test_invalid_position():

    game = GameEngine()

    with pytest.raises(ValueError):
        game.step((5, 5))

    with pytest.raises(ValueError):
        game.step((-1, 0))


def test_occupied_cell():

    game = GameEngine()

    game.step((0, 0))
    game.step((1, 1))

    with pytest.raises(ValueError):
        game.step((0, 0))


def test_wrong_action_format():

    game = GameEngine()

    with pytest.raises(ValueError):
        game.step((0, 0, 1))

    with pytest.raises(ValueError):
        game.step("00")

    with pytest.raises(ValueError):
        game.step((True, 0))


def test_x_wins():

    game = GameEngine()

    moves = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (0, 3)
    ]

    for move in moves:
        game.step(move)

    assert game.result() == "X"
    assert game.is_terminal()


def test_o_wins():

    game = GameEngine()

    moves = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (2, 3),
        (1, 3)
    ]

    for move in moves:
        game.step(move)

    assert game.result() == "O"
    assert game.is_terminal()


def test_draw():

    game = GameEngine()

    game.state.board = [
        [1, 1, -1, -1],
        [-1, -1, 1, 1],
        [1, -1, 1, -1],
        [-1, 1, -1, 1]
    ]

    game.state.move_count = 16

    assert game.result() == "DRAW"
    assert game.is_terminal()


def test_undo():

    game = GameEngine()

    game.step((0, 0))
    game.step((1, 1))

    assert game.undo() is True

    assert game.state.board[1][1] == EMPTY

    assert game.state.current_player == O

    assert game.state.move_count == 1


def test_clone():

    game = GameEngine()

    game.step((0, 0))

    copied_game = game.clone()

    copied_game.step((1, 1))

    assert game.state.board[1][1] == EMPTY

    assert copied_game.state.board[1][1] == O


def test_no_move_after_terminal():

    game = GameEngine()

    moves = [
        (0, 0),
        (1, 0),
        (0, 1),
        (1, 1),
        (0, 2),
        (1, 2),
        (0, 3)
    ]

    for move in moves:
        game.step(move)

    with pytest.raises(ValueError):
        game.step((2, 2))


def test_invalid_configuration():

    with pytest.raises(ValueError):
        GameEngine(board_size=0)

    with pytest.raises(ValueError):
        GameEngine(board_size=4, win_length=5)
