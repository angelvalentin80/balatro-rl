"""
Neural network policy for Balatro RL agent
"""

import torch
import torch.nn as nn
import numpy as np
from typing import Dict, Any

class BalatroPolicy(nn.Module):
    """
    Neural network policy for Balatro decision making
    """
    
    def __init__(self, state_dim: int = 128, action_dim: int = 64, hidden_dim: int = 256):
        super().__init__()
        
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # Feature extraction layers
        self.feature_net = nn.Sequential(
            nn.Linear(state_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU()
        )
        
        # Action value head
        self.value_head = nn.Linear(hidden_dim, 1)
        
        # Action probability head
        self.action_head = nn.Linear(hidden_dim, action_dim)
        
    def forward(self, state: torch.Tensor) -> tuple[torch.Tensor, torch.Tensor]:
        """
        Forward pass through the network
        
        Args:
            state: Game state tensor
            
        Returns:
            Tuple of (action_logits, state_value)
        """
        features = self.feature_net(state)
        
        action_logits = self.action_head(features)
        state_value = self.value_head(features)
        
        return action_logits, state_value
    
    def get_action(self, state: np.ndarray, available_actions: list) -> tuple[int, float]:
        """
        Get action from policy given current state
        
        Args:
            state: Current game state as numpy array
            available_actions: List of available action indices
            
        Returns:
            Tuple of (action_index, action_probability)
        """
        with torch.no_grad():
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            action_logits, _ = self.forward(state_tensor)
            
            # Mask unavailable actions
            masked_logits = action_logits.clone()
            if available_actions:
                mask = torch.full_like(action_logits, float('-inf'))
                mask[0, available_actions] = 0
                masked_logits = action_logits + mask
            
            # Get action probabilities
            action_probs = torch.softmax(masked_logits, dim=-1)
            
            # Sample action
            action_dist = torch.distributions.Categorical(action_probs)
            action = action_dist.sample()
            
            return action.item(), action_probs[0, action].item()