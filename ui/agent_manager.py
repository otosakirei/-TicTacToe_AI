
import os
import numpy as np
import torch

from agents.random_agent import RandomAgent
from agents.heuristic_agent import HeuristicAgent
from agents.minimax_agent import MinimaxAgent
from agents.alphabeta_agent import AlphaBetaAgent
from agents.mcts_agent import MCTSAgent
from agents.dqn_agent import DQNAgent


class AgentManager:

    def __init__(self, model_path=None):

        # ==================================
        # KHỞI TẠO 5 AI AGENT THÔNG THƯỜNG
        # ==================================

        self.agents = {
            "Random": RandomAgent(),
            "Heuristic": HeuristicAgent(),
            "Minimax": MinimaxAgent(depth=4),
            "Alpha-Beta": AlphaBetaAgent(depth=4),
            "MCTS": MCTSAgent(simulations=1000)
        }

        # ==================================
        # KHỞI TẠO DQN
        # ==================================

        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        self.dqn_agent = DQNAgent(
            state_size=16,
            action_size=16,
            epsilon=0.0,
            device=self.device
        )

        if model_path is None:
            project_root = os.path.dirname(
                os.path.dirname(os.path.abspath(__file__))
            )

            model_path = os.path.join(
                project_root,
                "models",
                "dqn_tictactoe.pth"
            )

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Không tìm thấy mô hình DQN: {model_path}"
            )

        checkpoint = torch.load(
            model_path,
            map_location=self.device,
            weights_only=True
        )

        self.dqn_agent.policy_net.load_state_dict(checkpoint)
        self.dqn_agent.policy_net.eval()

        self.agents["DQN"] = self.dqn_agent

        print("Agent Manager initialized!")
        print("Device:", self.device)
        print("Available Agents:", list(self.agents.keys()))

    # ==================================
    # LẤY DANH SÁCH AI
    # ==================================

    def get_agent_names(self):
        return list(self.agents.keys())

    # ==================================
    # CHỌN NƯỚC ĐI
    # ==================================

    def get_action(self, game, agent_name):

        if agent_name not in self.agents:
            raise ValueError(
                f"Agent không tồn tại: {agent_name}"
            )

        # Lấy các nước đi hợp lệ
        legal_actions = game.legal_actions()

        if not legal_actions:
            return None

        # ==================================
        # DQN
        # ==================================

        if agent_name == "DQN":

            board = np.array(
                game.state.board,
                dtype=np.float32
            )

            player = game.state.current_player

            # Mã hóa trạng thái theo góc nhìn người chơi hiện tại
            state = (
                board.flatten() * player
            ).astype(np.float32)

            # Chuyển tọa độ thành chỉ số 0-15
            legal_indices = [
                row * 4 + col
                for row, col in legal_actions
            ]

            action_index = self.dqn_agent.choose_action(
                state,
                legal_indices,
                training=False
            )

            if action_index not in legal_indices:
                raise ValueError(
                    f"DQN trả về nước đi không hợp lệ: {action_index}"
                )

            action = (
                action_index // 4,
                action_index % 4
            )

        # ==================================
        # 5 AGENT CÒN LẠI
        # ==================================

        else:

            agent = self.agents[agent_name]

            action = agent.choose_action(game)

        # ==================================
        # KIỂM TRA NƯỚC ĐI
        # ==================================

        if action not in legal_actions:
            raise ValueError(
                f"{agent_name} chọn nước đi không hợp lệ: {action}"
            )

        return action

    # ==================================
    # ĐỔI AI
    # ==================================

    def reset_agents(self):
        self.dqn_agent.epsilon = 0.0
        self.dqn_agent.policy_net.eval()
