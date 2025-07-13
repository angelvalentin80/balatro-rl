"""
Training logic for Balatro RL agent
"""

import torch
import torch.optim as optim
import numpy as np
from typing import Dict, List, Any
from .policy import BalatroPolicy
import logging

class BalatroTrainer:
    """
    Handles training of the Balatro RL agent
    """
    
    def __init__(self, policy: BalatroPolicy, learning_rate: float = 3e-4):
        self.policy = policy
        self.optimizer = optim.Adam(policy.parameters(), lr=learning_rate)
        self.logger = logging.getLogger(__name__)
        
        # Training buffers
        self.states = []
        self.actions = []
        self.rewards = []
        self.values = []
        self.log_probs = []
        
    def collect_experience(self, state: np.ndarray, action: int, reward: float, 
                          value: float, log_prob: float):
        """
        Collect experience for training
        
        Args:
            state: Game state
            action: Action taken
            reward: Reward received
            value: State value estimate
            log_prob: Log probability of action
        """
        self.states.append(state)
        self.actions.append(action)
        self.rewards.append(reward)
        self.values.append(value)
        self.log_probs.append(log_prob)
    
    def compute_returns(self, next_value: float = 0.0, gamma: float = 0.99) -> List[float]:
        """
        Compute discounted returns
        
        Args:
            next_value: Value of next state (for bootstrapping)
            gamma: Discount factor
            
        Returns:
            List of discounted returns
        """
        returns = []
        R = next_value
        
        for reward in reversed(self.rewards):
            R = reward + gamma * R
            returns.insert(0, R)
            
        return returns
    
    def update_policy(self, gamma: float = 0.99, entropy_coef: float = 0.01,
                     value_coef: float = 0.5) -> Dict[str, float]:
        """
        Update policy using collected experience
        
        Args:
            gamma: Discount factor
            entropy_coef: Entropy regularization coefficient
            value_coef: Value loss coefficient
            
        Returns:
            Dictionary of training metrics
        """
        if not self.states:
            return {}
        
        # Convert to tensors
        states = torch.FloatTensor(np.array(self.states))
        actions = torch.LongTensor(self.actions)
        old_log_probs = torch.FloatTensor(self.log_probs)
        values = torch.FloatTensor(self.values)
        
        # Compute returns
        returns = self.compute_returns(gamma=gamma)
        returns = torch.FloatTensor(returns)
        
        # Compute advantages
        advantages = returns - values
        advantages = (advantages - advantages.mean()) / (advantages.std() + 1e-8)
        
        # Forward pass
        action_logits, new_values = self.policy(states)
        
        # Compute losses
        action_dist = torch.distributions.Categorical(logits=action_logits)
        new_log_probs = action_dist.log_prob(actions)
        entropy = action_dist.entropy().mean()
        
        # Policy loss (PPO-style, but simplified)
        ratio = torch.exp(new_log_probs - old_log_probs)
        policy_loss = -(ratio * advantages).mean()
        
        # Value loss
        value_loss = torch.nn.functional.mse_loss(new_values.squeeze(), returns)
        
        # Total loss
        total_loss = policy_loss + value_coef * value_loss - entropy_coef * entropy
        
        # Update
        self.optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(self.policy.parameters(), 0.5)
        self.optimizer.step()
        
        # Clear buffers
        self.clear_buffers()
        
        # Return metrics
        return {
            'policy_loss': policy_loss.item(),
            'value_loss': value_loss.item(),
            'entropy': entropy.item(),
            'total_loss': total_loss.item()
        }
    
    def clear_buffers(self):
        """Clear experience buffers"""
        self.states.clear()
        self.actions.clear()
        self.rewards.clear()
        self.values.clear()
        self.log_probs.clear()
    
    def save_model(self, path: str):
        """Save model checkpoint"""
        torch.save({
            'policy_state_dict': self.policy.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict()
        }, path)
        self.logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str):
        """Load model checkpoint"""
        checkpoint = torch.load(path)
        self.policy.load_state_dict(checkpoint['policy_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.logger.info(f"Model loaded from {path}")