"""
Balatro Reward System - Ante 1 Focused

Simple reward system focused on teaching the AI to consistently beat
the 300-chip small blind in ante 1. No complex scaling, just core fundamentals.
"""

from typing import Dict, Any

class BalatroRewardCalculator:
    """
    Focused reward calculator for ante 1 mastery.
    
    Goal: Teach AI to consistently score 300+ chips to beat small blind.
    Strategy: Reward consistent 75+ point hands, not risky high hands.
    """
    
    def __init__(self):
        self.previous_chips = 0
        self.previous_hand_played = "None"
        self.blind_already_defeated = False
        
        # Episode tracking for win logging
        self.episode_count = 0
        self.wins = 0
        self.hands_played = []  # Track each hand in current episode
        self.episode_total_reward = 0
        self.last_seen_hand_type = 'Unknown'  # Store hand type when we see it
        self.winning_chips = 0  # Store chips when blind is defeated
        
        # Percentage-based reward thresholds (% of blind requirement)
        self.REWARD_THRESHOLDS = {
            "excellent": 80.0,  # 80%+ of blind requirement
            "good": 50.0,       # 50-79% of blind requirement  
            "decent": 25.0      # 25-49% of blind requirement
        }
        
    def calculate_reward(self, current_state: Dict[str, Any], 
                        prev_state: Dict[str, Any] = None) -> float:
        """Simple reward focused on ante 1 small blind success"""
        reward = 0.0
        reward_breakdown = []  # Track all reward components
        
        inner_game_state = current_state.get('game_state', {})
        
        # Extract key metrics
        current_chips = inner_game_state.get('chips', 0)
        game_over = inner_game_state.get('game_over', 0)
        retry_count = inner_game_state.get('retry_count', 0)
        
        # === RETRY PENALTY ===
        # Negative reward for invalid actions that require retries
        if retry_count > 0:
            retry_penalty = -0.1 * retry_count  # -0.1 per retry
            reward += retry_penalty
            reward_breakdown.append(f"retry_penalty: {retry_penalty:.2f} (retries: {retry_count})")
        
        # Check if blind is defeated by comparing chips to requirement
        blind_chips = inner_game_state.get('blind_chips', 300) # TODO 300 only focusing on first blind
        # Only consider blind defeated if we actually have chips AND a valid blind requirement
        blind_defeated = inner_game_state.get('game_win', 0)
        
        
        # Hand type info - use current hand scoring
        current_hand_info = inner_game_state.get('current_hand', {})
        current_hand_played = current_hand_info.get('handname', 'None')
        
        # Store hand type when we see it (for later use when chips change)
        if current_hand_played and current_hand_played != 'None' and current_hand_played != '':
            self.last_seen_hand_type = current_hand_played
        
        # === CORE SCORING REWARDS ===
        # Reward good hands (chip increases) based on % of blind requirement
        chip_gain = current_chips - self.previous_chips
        if chip_gain > 0 and game_over == 0 and not self.blind_already_defeated and blind_chips > 0:
            # Track this hand for episode logging (use stored hand type)
            # Only track if blind not already defeated
            hand_type_to_use = getattr(self, 'last_seen_hand_type', 'Unknown')
            self._track_hand_played(chip_gain, hand_type_to_use, current_chips)
            
            # Calculate percentage of blind requirement this hand achieved
            chip_percentage = (chip_gain / blind_chips) * 100
            
            if chip_percentage >= self.REWARD_THRESHOLDS["excellent"]:
                reward += 10.0
                reward_breakdown.append(f"Excellent hand (+{chip_gain} chips, {chip_percentage:.1f}% of blind): +10.0")
            elif chip_percentage >= self.REWARD_THRESHOLDS["good"]:
                reward += 4.0
                reward_breakdown.append(f"Good hand (+{chip_gain} chips, {chip_percentage:.1f}% of blind): +4.0")
            elif chip_percentage >= self.REWARD_THRESHOLDS["decent"]:
                reward += 1.0
                reward_breakdown.append(f"Decent hand (+{chip_gain} chips, {chip_percentage:.1f}% of blind): +1.0")
            else:
                reward += 0.5
                reward_breakdown.append(f"Small hand (+{chip_gain} chips, {chip_percentage:.1f}% of blind): +0.5")
        
        # === REMOVED HAND TYPE REWARDS ===
        # Hand type rewards removed - in Balatro, only chips matter!
        # A High Card scoring 300 chips beats a Full House scoring 100 chips
                
        # === BLIND COMPLETION ===
        # Main goal - beat the blind (only reward once per episode)
        if blind_defeated and not self.blind_already_defeated and game_over == 0:
            reward += 50.0  # SUCCESS! Normalized from +500 to +50
            reward_breakdown.append(f"BLIND DEFEATED: +50.0")
            self.blind_already_defeated = True
            self.winning_chips = current_chips  # Store winning chip count
            
        # === PENALTIES ===
        # Game over penalty - ONLY for actual losses (blind not defeated)
        if game_over == 1 and not hasattr(self, 'game_over_penalty_applied') and not self.blind_already_defeated:
            reward -= 20.0  # Normalized from -200 to -20
            reward_breakdown.append("Game over: -20.0")
            self.game_over_penalty_applied = True
            
        # Track episode total reward
        self.episode_total_reward += reward
        
        # Keep only essential logging - no step-by-step reward breakdown
        
        # Update tracking
        self.previous_chips = current_chips
        self.previous_hand_played = current_hand_played
        
        return reward
    
    def reset(self):
        """Reset for new episode - log win details if episode was won"""
        self.episode_count += 1
        
        # Check if this episode was a win and log details
        if self.blind_already_defeated:
            self.wins += 1
            self._log_episode_win()
            
            # Show win rate on every win for immediate feedback
            self._log_win_rate()
        
        # Reset for next episode
        self.previous_chips = 0
        self.previous_hand_played = "None"
        self.blind_already_defeated = False
        self.hands_played = []
        self.episode_total_reward = 0
        self.last_seen_hand_type = 'Unknown'
        self.winning_chips = 0
        # Reset game over penalty flag
        if hasattr(self, 'game_over_penalty_applied'):
            delattr(self, 'game_over_penalty_applied')

    def _log_episode_win(self):
        """Log detailed breakdown of winning episode"""
        final_chips = self.winning_chips if self.winning_chips > 0 else (max([hand['total_chips'] for hand in self.hands_played]) if self.hands_played else 0)
        
        # Episode summary
        print(f"🎯 EPISODE {self.episode_count} COMPLETE: WON with {final_chips} chips in {len(self.hands_played)} hands | Total reward: {self.episode_total_reward:.1f}")
        
        # Hand-by-hand breakdown
        for i, hand in enumerate(self.hands_played, 1):
            print(f"   Hand {i}: {hand['hand_type']} (+{hand['chips']} chips, total: {hand['total_chips']})")
    
    def _log_win_rate(self):
        """Log win rate statistics"""
        win_rate = (self.wins / self.episode_count) * 100
        print(f"📊 Episode {self.episode_count}: {self.wins} wins ({win_rate:.1f}%) | Last 100: TBD")
    
    def _track_hand_played(self, chip_gain, current_hand_played, current_chips):
        """Track hand details for episode logging"""
        hand_info = {
            'chips': chip_gain,
            'hand_type': current_hand_played if current_hand_played != "None" else "Unknown",
            'total_chips': current_chips
        }
        self.hands_played.append(hand_info)