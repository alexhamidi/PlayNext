from torch import nn
import torch
import numpy as np

class SongClassifier(nn.Module):
    def __init__(self, n_features, n_classes):
        super().__init__()
        self.linear_layer_1 = nn.Linear(n_features, 8)
        self.linear_layer_2 = nn.Linear(8, n_classes)

    def forward(self, features):
        x = torch.relu(self.linear_layer_1(features))
        return self.linear_layer_2(x)
