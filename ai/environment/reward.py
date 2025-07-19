"""
Balatro Reward System - The Expert on What's Good/Bad

This module is the single source of truth for reward calculation in Balatro RL.
All reward logic is centralized here to make experimentation and tuning easier.

The BalatroRewardCalculator analyzes game state changes and assigns rewards
that teach the AI what constitutes good vs bad Balatro gameplay.
"""

from typing import Dict, Any
import numpy as np

class BalatroRewardCalculator:
    """
    Expert reward calculator for Balatro RL training
    
    This is the single authority on what constitutes good/bad play in Balatro.
    Centralizes all reward logic for easy experimentation and tuning.
    
    Reward philosophy:
    - Positive rewards for progress (chips, rounds, money)
    - Bonus rewards for efficiency (fewer hands/discards used)  
    - Large rewards for major milestones (completing antes)
    - Negative rewards for game over (based on progress made)
    """
    
    def __init__(self):
        self.chips = 0
        
    def calculate_reward(self, current_state: Dict[str, Any], 
                        prev_state: Dict[str, Any] = None) -> float:
        """
        Main reward calculation method - analyzes state changes and assigns rewards
        
        This is the core method that determines what the AI should optimize for.
        Examines differences between previous and current game state to calculate
        appropriate rewards for the action that caused the transition.
        
        Args:
            current_state: Current Balatro game state
            prev_state: Previous Balatro game state (None for first step)
            
        Returns:
            Float reward value (positive = good, negative = bad, zero = neutral)
        """
        reward = 0.0
        
        # Extract relevant metrics
        current_chips = current_state.get('chips', 0)
        game_over = current_state.get('game_over', False) #TODO fix
        
        # Score-based rewards
        chip_diff = current_chips - self.chips
        if chip_diff > 0:
            reward += chip_diff * 0.001  # Small reward for score increases
        
        # Game over penalty
        if game_over:
            # Penalty based on how early the game ended
            # max_ante = 8  # Typical max ante in Balatro
            # completion_ratio = current_ante / max_ante
            # reward += completion_ratio * 100.0  # Reward based on progress
            reward -= 10 #TODO keeping this simple for now
            
        # Update previous state
        self.chips = current_chips
        
        return reward
    
    def reset(self):
        """
        Reset reward calculator state for new episode
        
        Called at the start of each new Balatro run to clear
        previous state tracking variables.
        """
        self.chips = 0
    
    def get_shaped_reward(self, state: Dict[str, Any], action: str) -> float:
        """
        Calculate action-specific reward shaping
        
        Provides small rewards/penalties for specific actions to guide
        AI behavior beyond just game state changes. Use sparingly to
        avoid overriding the main reward signal.
        
        Args:
            state: Current game state when action was taken
            action: Action that was taken (for action-specific rewards)
            
        Returns:
            Small shaped reward value (usually -1 to +1)
        """
        # TODO look at this this could help but currently not in a working state
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
