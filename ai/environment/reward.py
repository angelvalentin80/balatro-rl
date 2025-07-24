"""
Balatro Reward System - The Expert on What's Good/Bad

This module is the single source of truth for reward calculation in Balatro RL.
All reward logic is centralized here to make experimentation and tuning easier.

The BalatroRewardCalculator analyzes game state changes and assigns rewards
that teach the AI what constitutes good vs bad Balatro gameplay.
"""

from typing import Dict, Any
import math

from numpy import inner

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
        self.ante = 0
        
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

        # Small step penalty to encourage episode completion
        reward -= 0.01

        inner_game_state = current_state.get('game_state', {})
        retry_count = current_state.get('retry_count', 0)
        
        # Extract relevant metrics
        current_chips = inner_game_state.get('chips', 0)
        game_over = inner_game_state.get('game_over', 0)
        state = inner_game_state.get('state', 0)
        # Ante
        ante_info = inner_game_state.get('ante', {})
        current_ante = ante_info.get('current_ante', 0)
        win_ante = ante_info.get('win_ante', 0)
        # Blind info
        blind_info = inner_game_state.get('blind', {})
        blind_defeated = blind_info.get('defeated', False)
        # Round info for discard tracking
        round_info = inner_game_state.get('round', {})
        discards_left = round_info.get('discards_left', 0)
        
        
        # Chip-based rewards - DISABLED to focus on blind completion only
        # chip_diff = current_chips - self.chips
        # if chip_diff > 0:
        #     reward += math.log(chip_diff + 1) * 0.1

        # Ante based rewards
        ante_diff = current_ante - self.ante
        if ante_diff > 0:
            reward += ante_diff * 50.0  # Large reward for completing antes
            
        # Blind defeat rewards - HUGE reward for winning rounds!
        if state == 8 and blind_defeated:  # ROUND_EVAL state with defeated blind
            reward += 200.0  # Massive reward for beating a blind!
            
        # Penalty for not using discards (encourages hand formulation)
        if discards_left > 0:
            reward -= discards_left * 1.0  # Light penalty for unused discards
        
        # Game over penalty
        if game_over == 1:
            # Penalty based on how early the game ended
            completion_ratio = current_ante / win_ante if win_ante > 0 else 0
            reward -= 50.0  # Base penalty for dying
            reward += completion_ratio * 30.0  # Partial credit for progress (still net negative)
            
            # Episode completion bonus - reward for completing any antes
            if current_ante >= 1:
                reward += 100.0  # Bonus for making progress before game over

        # Wrong move penalty - reduced to encourage exploration
        if retry_count > 0:
            reward -= 0.01 * retry_count  # Reduced from 0.1 to encourage exploration
            
        # Update previous state
        self.chips = current_chips
        self.ante = current_ante
        
        return reward
    
    def reset(self):
        """
        Reset reward calculator state for new episode
        
        Called at the start of each new Balatro run to clear
        previous state tracking variables.
        """
        self.chips = 0
        self.ante = 0
    
