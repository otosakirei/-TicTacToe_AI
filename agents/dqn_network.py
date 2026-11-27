
import torch
import torch.nn as nn


class DQNNetwork(nn.Module):
    """
    Neural Network dành cho Tic-Tac-Toe 4x4.

    Input:  16 giá trị trạng thái bàn cờ.
    Output: 16 Q-values tương ứng 16 hành động.
    """

    def __init__(self, state_size=16, action_size=16):
        super(DQNNetwork, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(state_size, 128),
            nn.ReLU(),

            nn.Linear(128, 128),
            nn.ReLU(),

            nn.Linear(128, action_size)
        )

    def forward(self, state):
        return self.network(state)
