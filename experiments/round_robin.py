
import os
import csv
import json
import time
import random
import itertools

import numpy as np
import torch

from game.game_engine import GameEngine
from ui.agent_manager import AgentManager


# =========================================================
# CẤU HÌNH
# =========================================================

BOARD_SIZE = 4
WIN_LENGTH = 4

DEFAULT_GAMES_PER_PAIR = 100
DEFAULT_SEED = 42

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_DIR = os.path.join(
    PROJECT_ROOT,
    "results"
)


# =========================================================
# HỖ TRỢ REPRODUCIBILITY
# =========================================================

def set_random_seed(seed, agent_manager=None):
    """
    Thiết lập seed cho Python, NumPy, PyTorch
    và các MCTS agent có random generator riêng.
    """

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)

    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

    if agent_manager is not None:
        mcts = agent_manager.agents.get("MCTS")

        if mcts is not None:
            # Hỗ trợ trường hợp MCTS dùng random.Random riêng.
            rng = getattr(mcts, "rng", None)

            if rng is not None and hasattr(rng, "seed"):
                rng.seed(seed)


# =========================================================
# LẤY THỐNG KÊ AGENT
# =========================================================

def get_agent_stats(agent_manager, agent_name):
    """
    Lấy thống kê tìm kiếm nếu agent có hỗ trợ.
    Agent không có thống kê sẽ trả về dictionary rỗng.
    """

    agent = agent_manager.agents[agent_name]

    if hasattr(agent, "get_search_stats"):
        stats = agent.get_search_stats()

        if isinstance(stats, dict):
            return stats

    stats = getattr(agent, "last_search_stats", None)

    if isinstance(stats, dict):
        return stats

    return {}


# =========================================================
# CHẠY MỘT VÁN ĐẤU
# =========================================================

def play_one_game(
    agent_manager,
    agent_x,
    agent_o,
    game_id,
    seed
):
    """
    agent_x: AI cầm X và đi trước.
    agent_o: AI cầm O và đi sau.

    Trả về:
        match_result: thông tin kết quả ván.
        move_records: thông tin từng nước đi.
    """

    set_random_seed(seed, agent_manager)

    agent_manager.reset_agents()

    game = GameEngine(
        board_size=BOARD_SIZE,
        win_length=WIN_LENGTH
    )

    move_records = []
    move_number = 0

    game_start = time.perf_counter()

    while not game.is_terminal():

        current_player = game.get_current_player()

        if current_player == "X":
            current_agent = agent_x
        else:
            current_agent = agent_o

        # Thời gian suy nghĩ của AI
        decision_start = time.perf_counter()

        action = agent_manager.get_action(
            game,
            current_agent
        )

        decision_time = (
            time.perf_counter() - decision_start
        )

        # Lấy thống kê ngay sau khi AI chọn nước đi
        agent_stats = get_agent_stats(
            agent_manager,
            current_agent
        )

        # Thực hiện nước đi
        game.step(action)

        move_number += 1

        move_records.append({
            "game_id": game_id,
            "move_number": move_number,
            "player": current_player,
            "agent": current_agent,
            "row": action[0],
            "col": action[1],
            "decision_time": decision_time,
            "stats_json": json.dumps(
                agent_stats,
                ensure_ascii=False,
                default=str
            )
        })

    game_time = time.perf_counter() - game_start

    result = game.result()

    if result == "X":
        winner = agent_x
    elif result == "O":
        winner = agent_o
    else:
        winner = "DRAW"

    match_result = {
        "game_id": game_id,
        "seed": seed,
        "agent_x": agent_x,
        "agent_o": agent_o,
        "winner": winner,
        "result": result,
        "total_moves": move_number,
        "game_time": game_time
    }

    return match_result, move_records


# =========================================================
# TỔNG HỢP KẾT QUẢ
# =========================================================

def calculate_summary(match_records, agent_names):
    """
    Tính W/D/L và Score cho từng AI.
    Score = (Win + 0.5 * Draw) / Total Games
    """

    summary = {}

    for name in agent_names:

        wins = 0
        draws = 0
        losses = 0

        for match in match_records:

            if match["agent_x"] != name and match["agent_o"] != name:
                continue

            if match["winner"] == "DRAW":
                draws += 1

            elif match["winner"] == name:
                wins += 1

            else:
                losses += 1

        total = wins + draws + losses

        score = (
            (wins + 0.5 * draws) / total
            if total > 0 else 0
        )

        summary[name] = {
            "agent": name,
            "wins": wins,
            "draws": draws,
            "losses": losses,
            "games": total,
            "score": score,
            "win_rate": wins / total if total else 0,
            "draw_rate": draws / total if total else 0,
            "loss_rate": losses / total if total else 0
        }

    return list(summary.values())


# =========================================================
# LƯU CSV
# =========================================================

def save_csv(records, filepath):

    if not records:
        print("Không có dữ liệu để lưu:", filepath)
        return

    os.makedirs(
        os.path.dirname(filepath),
        exist_ok=True
    )

    fieldnames = list(records[0].keys())

    with open(
        filepath,
        mode="w",
        newline="",
        encoding="utf-8-sig"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        writer.writeheader()
        writer.writerows(records)

    print("Đã lưu:", filepath)


# =========================================================
# ROUND-ROBIN TOURNAMENT
# =========================================================

def run_tournament(
    agent_manager=None,
    games_per_pair=DEFAULT_GAMES_PER_PAIR,
    seed=DEFAULT_SEED,
    selected_agents=None
):
    """
    Thi đấu vòng tròn giữa các AI.

    Mỗi cặp AI được thi đấu games_per_pair ván.
    Số ván được chia đều giữa hai bên cầm X và O.
    """

    if games_per_pair < 2 or games_per_pair % 2 != 0:
        raise ValueError(
            "games_per_pair phải là số chẵn và >= 2."
        )

    if agent_manager is None:
        agent_manager = AgentManager()

    if selected_agents is None:
        selected_agents = agent_manager.get_agent_names()

    for name in selected_agents:
        if name not in agent_manager.agents:
            raise ValueError(f"Không tìm thấy agent: {name}")

    pairs = list(
        itertools.combinations(selected_agents, 2)
    )

    total_games = len(pairs) * games_per_pair

    match_records = []
    move_records = []

    game_id = 0

    print("=" * 60)
    print("ROUND-ROBIN TOURNAMENT")
    print("=" * 60)
    print("Agents:", selected_agents)
    print("Số cặp đấu:", len(pairs))
    print("Số ván mỗi cặp:", games_per_pair)
    print("Tổng số ván:", total_games)
    print("=" * 60)

    tournament_start = time.perf_counter()

    for pair_index, (agent_a, agent_b) in enumerate(pairs, start=1):

        print(
            f"\n[{pair_index}/{len(pairs)}] "
            f"{agent_a} vs {agent_b}"
        )

        # Một nửa số ván: A cầm X
        # Một nửa số ván: B cầm X
        games_each_side = games_per_pair // 2

        for game_index in range(games_per_pair):

            if game_index < games_each_side:
                agent_x = agent_a
                agent_o = agent_b
            else:
                agent_x = agent_b
                agent_o = agent_a

            game_id += 1

            game_seed = seed + game_id

            match_result, game_moves = play_one_game(
                agent_manager=agent_manager,
                agent_x=agent_x,
                agent_o=agent_o,
                game_id=game_id,
                seed=game_seed
            )

            match_records.append(match_result)
            move_records.extend(game_moves)

            print(
                f"  Game {game_index + 1:03d}/{games_per_pair}: "
                f"X={agent_x:<10} "
                f"O={agent_o:<10} "
                f"Winner={match_result['winner']}"
            )

    tournament_time = (
        time.perf_counter() - tournament_start
    )

    summary_records = calculate_summary(
        match_records,
        selected_agents
    )

    # Lưu kết quả
    os.makedirs(RESULTS_DIR, exist_ok=True)

    save_csv(
        match_records,
        os.path.join(RESULTS_DIR, "match_results.csv")
    )

    save_csv(
        move_records,
        os.path.join(RESULTS_DIR, "move_results.csv")
    )

    save_csv(
        summary_records,
        os.path.join(RESULTS_DIR, "agent_summary.csv")
    )

    # Thông tin cấu hình thí nghiệm
    metadata = {
        "board_size": BOARD_SIZE,
        "win_length": WIN_LENGTH,
        "games_per_pair": games_per_pair,
        "agents": selected_agents,
        "number_of_pairs": len(pairs),
        "total_games": total_games,
        "seed": seed,
        "tournament_time_seconds": tournament_time,
        "device": str(agent_manager.device)
    }

    metadata_path = os.path.join(
        RESULTS_DIR,
        "tournament_metadata.json"
    )

    with open(
        metadata_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            metadata,
            file,
            ensure_ascii=False,
            indent=4
        )

    print("\n" + "=" * 60)
    print("TOURNAMENT COMPLETED")
    print("=" * 60)

    print("Tổng số ván:", len(match_records))
    print(f"Thời gian: {tournament_time:.2f} giây")

    print("\nBẢNG XẾP HẠNG")

    summary_records.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    for index, item in enumerate(summary_records, start=1):

        print(
            f"{index}. {item['agent']:<12} "
            f"W={item['wins']:<4} "
            f"D={item['draws']:<4} "
            f"L={item['losses']:<4} "
            f"Score={item['score']:.3f}"
        )

    return {
        "matches": match_records,
        "moves": move_records,
        "summary": summary_records,
        "metadata": metadata
    }


# =========================================================
# CHẠY TRỰC TIẾP FILE
# =========================================================

if __name__ == "__main__":

    manager = AgentManager()

    results = run_tournament(
        agent_manager=manager,
        games_per_pair=100,
        seed=42
    )
