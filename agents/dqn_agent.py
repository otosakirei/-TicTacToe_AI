
import random
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim

from agents.dqn_network import DQNNetwork
from agents.replay_buffer import ReplayBuffer


class DQNAgent:

    def __init__(
        self,
        state_size=16,
        action_size=16,
        learning_rate=0.001,
        gamma=0.99,
        epsilon=1.0,
        epsilon_min=0.05,
        epsilon_decay=0.995,
        buffer_capacity=10000,
        batch_size=64,
        device=None
    ):
        self.state_size = state_size
        self.action_size = action_size

        self.gamma = gamma
        self.epsilon = epsilon
        self.epsilon_min = epsilon_min
        self.epsilon_decay = epsilon_decay
        self.batch_size = batch_size

        self.device = torch.device(
            device if device else
            ("cuda" if torch.cuda.is_available() else "cpu")
        )

        # Policy Network
        self.policy_net = DQNNetwork(
            state_size, action_size
        ).to(self.device)

        # Target Network
        self.target_net = DQNNetwork(
            state_size, action_size
        ).to(self.device)

        self.target_net.load_state_dict(
            self.policy_net.state_dict()
        )

        self.target_net.eval()

        # Optimizer và Loss
        self.optimizer = optim.Adam(
            self.policy_net.parameters(),
            lr=learning_rate
        )
        self.loss_fn = torch.nn.SmoothL1Loss()

        self.loss_function = nn.SmoothL1Loss()

        # Experience Replay
        self.memory = ReplayBuffer(buffer_capacity)

    def choose_action(self, state, legal_actions, training=True):
        """
        Epsilon-Greedy:
        - Khám phá: chọn ngẫu nhiên.
        - Khai thác: chọn Q-value cao nhất.
        """

        legal_actions = list(legal_actions)

        if not legal_actions:
            raise ValueError("Không còn nước đi hợp lệ!")

        if training and random.random() < self.epsilon:
            return random.choice(legal_actions)

        state_tensor = torch.tensor(
            state, dtype=torch.float32
        ).unsqueeze(0).to(self.device)

        self.policy_net.eval()

        with torch.no_grad():
            q_values = self.policy_net(state_tensor)[0]

        self.policy_net.train()

        # Chỉ xét các hành động hợp lệ
        legal_q_values = q_values[legal_actions]

        best_index = torch.argmax(legal_q_values).item()

        return legal_actions[best_index]

    def remember(self, state, action, reward, next_state, done):
        self.memory.push(
            state, action, reward, next_state, done
        )

    
    def train_step(self):
        if len(self.memory) < self.batch_size:
            return None
    
        states, actions, rewards, next_states, dones = self.memory.sample(
            self.batch_size
        )
    
        states = torch.tensor(states, dtype=torch.float32, device=self.device)
        actions = torch.tensor(actions, dtype=torch.long, device=self.device)
        rewards = torch.tensor(rewards, dtype=torch.float32, device=self.device)
        next_states = torch.tensor(
            next_states, dtype=torch.float32, device=self.device
        )
        dones = torch.tensor(dones, dtype=torch.float32, device=self.device)
    
        # Q-value của hành động DQN đã thực hiện
        current_q = self.policy_net(states).gather(
            1, actions.unsqueeze(1)
        ).squeeze(1)
    
        # Tính Q-value mục tiêu, không tính các ô đã được đánh
        with torch.no_grad():
            next_q_values = self.target_net(next_states)
    
            legal_mask = (next_states == 0)
            has_legal_action = legal_mask.any(dim=1)
    
            next_q_values = next_q_values.masked_fill(
                ~legal_mask, -1e9
            )
    
            next_q = next_q_values.max(dim=1)[0]
    
            # Nếu không còn nước đi hoặc ván đã kết thúc,
            # giá trị tương lai bằng 0
            next_q = torch.where(
                has_legal_action,
                next_q,
                torch.zeros_like(next_q)
            )
            next_q = torch.where(
                dones.bool(),
                torch.zeros_like(next_q),
                next_q
            )
    
            target_q = rewards + self.gamma * next_q
    
        loss = self.loss_fn(current_q, target_q)
    
        self.optimizer.zero_grad()
        loss.backward()
    
        # Giới hạn gradient để quá trình học ổn định hơn
        torch.nn.utils.clip_grad_norm_(
            self.policy_net.parameters(), max_norm=1.0
        )
    
        self.optimizer.step()
    
        return loss.item()


    def update_target_network(self):
        self.target_net.load_state_dict(
            self.policy_net.state_dict()
        )

    def decay_epsilon(self):
        self.epsilon = max(
            self.epsilon_min,
            self.epsilon * self.epsilon_decay
        )
