"""
Reward calculation for Balatro RL environment
"""

from typing import Dict, Any
import numpy as np

class BalatroRewardCalculator:
    """
    Calculates rewards for Balatro RL training
    """
    
    def __init__(self):
        self.prev_score = 0
        self.prev_money = 0
        self.prev_round = 0
        self.prev_ante = 0
        
    def calculate_reward(self, current_state: Dict[str, Any], 
                        prev_state: Dict[str, Any] = None) -> float:
        """
        Calculate reward based on game state changes
        
        Args:
            current_state: Current game state
            prev_state: Previous game state (optional)
            
        Returns:
            Calculated reward
        """
        reward = 0.0
        
        # Extract relevant metrics
        current_score = current_state.get('score', 0)
        current_money = current_state.get('money', 0)
        current_round = current_state.get('round', 0)
        current_ante = current_state.get('ante', 0)
        game_over = current_state.get('game_over', False)
        
        # Score-based rewards
        score_diff = current_score - self.prev_score
        if score_diff > 0:
            reward += score_diff * 0.001  # Small reward for score increases
        
        # Money-based rewards
        money_diff = current_money - self.prev_money
        if money_diff > 0:
            reward += money_diff * 0.01  # Reward for gaining money
        
        # Round progression rewards
        if current_round > self.prev_round:
            reward += 10.0  # Big reward for completing rounds
        
        # Ante progression rewards
        if current_ante > self.prev_ante:
            reward += 50.0  # Very big reward for completing antes
        
        # Game over penalty
        if game_over:
            # Penalty based on how early the game ended
            max_ante = 8  # Typical max ante in Balatro
            completion_ratio = current_ante / max_ante
            reward += completion_ratio * 100.0  # Reward based on progress
            
        # Efficiency rewards (optional)
        # reward += self._calculate_efficiency_reward(current_state)
        
        # Update previous state
        self.prev_score = current_score
        self.prev_money = current_money
        self.prev_round = current_round
        self.prev_ante = current_ante
        
        return reward
    
    def _calculate_efficiency_reward(self, state: Dict[str, Any]) -> float:
        """
        Calculate rewards for efficient play
        
        Args:
            state: Current game state
            
        Returns:
            Efficiency reward
        """
        reward = 0.0
        
        # Reward for using fewer discards
        discards_remaining = state.get('discards', 0)
        if discards_remaining > 0:
            reward += discards_remaining * 0.1
        
        # Reward for using fewer hands
        hands_remaining = state.get('hands', 0)
        if hands_remaining > 0:
            reward += hands_remaining * 0.5
        
        return reward
    
    def reset(self):
        """Reset reward calculator for new episode"""
        self.prev_score = 0
        self.prev_money = 0
        self.prev_round = 0
        self.prev_ante = 0
    
    def get_shaped_reward(self, state: Dict[str, Any], action: str) -> float:
        """
        Get shaped reward based on specific actions
        
        Args:
            state: Current game state
            action: Action taken
            
        Returns:
            Shaped reward
        """
        reward = 0.0
        
        # Action-specific rewards
        if action == "play_hand":
            # Small reward for playing hands (encourages action)
            reward += 0.1
            
        elif action == "discard":
            # Very small reward for discarding (necessary but not preferred)
            reward += 0.01
            
        elif action == "skip_blind":
            # Penalty for skipping (unless justified)
            reward -= 1.0
            
        elif action == "buy_item":
            # Neutral - depends on if it's a good purchase
            reward += 0.0
            
        return reward