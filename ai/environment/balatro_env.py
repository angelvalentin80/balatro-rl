"""
Balatro RL Environment
Wraps the HTTP communication in a gym-like interface for RL training
"""

import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import logging

from ..utils.serialization import GameStateValidator


class BalatroEnvironment:
    """
    Gym-like environment interface for Balatro RL training
    
    This class will eventually wrap the HTTP communication
    and provide a standard RL interface with step(), reset(), etc.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.current_state = None
        self.game_over = False
        
        # TODO: Define action and observation spaces
        # self.action_space = ...
        # self.observation_space = ...
    
    def reset(self) -> Dict[str, Any]:
        """Reset the environment for a new episode"""
        self.current_state = None
        self.game_over = False
        
        # TODO: Send reset signal to Balatro mod
        # This might involve starting a new run
        
        return self._get_initial_state()
    
    def step(self, action: Dict[str, Any]) -> Tuple[Dict, float, bool, Dict]:
        """
        Take an action in the environment
        
        Args:
            action: Action to take
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        # TODO: Send action to Balatro via HTTP
        # TODO: Receive new game state
        # TODO: Calculate reward
        # TODO: Check if episode is done
        
        observation = self._process_game_state(self.current_state)
        reward = self._calculate_reward()
        done = self.game_over
        info = {}
        
        return observation, reward, done, info
    
    def _get_initial_state(self) -> Dict[str, Any]:
        """Get initial game state"""
        # TODO: Implement
        return {}
    
    def _process_game_state(self, raw_state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process raw game state into format suitable for RL agent
        
        This might involve:
        - Extracting relevant features
        - Normalizing values
        - Converting to numpy arrays
        """
        if not raw_state:
            return {}
        
        # Validate state structure
        try:
            GameStateValidator.validate_game_state(raw_state)
        except ValueError as e:
            self.logger.error(f"Invalid game state: {e}")
            return {}
        
        # TODO: Extract and process features
        processed = {
            'hand_features': self._extract_hand_features(raw_state.get('hand', {})),
            'game_features': self._extract_game_features(raw_state),
            'available_actions': raw_state.get('available_actions', [])
        }
        
        return processed
    
    def _extract_hand_features(self, hand: Dict[str, Any]) -> np.ndarray:
        """Extract numerical features from hand"""
        # TODO: Convert hand cards to numerical representation
        # This might include:
        # - Card values (2-14 for 2-A)
        # - Suits (0-3 for different suits)
        # - Special abilities/bonuses
        
        cards = hand.get('cards', [])
        features = []
        
        for card in cards:
            # Extract card features
            suit_encoding = self._encode_suit(card.get('suit', ''))
            value_encoding = self._encode_value(card.get('base', {}).get('value', ''))
            nominal = card.get('base', {}).get('nominal', 0)
            
            # Add ability features
            ability = card.get('ability', {})
            ability_features = [
                ability.get('t_chips', 0),
                ability.get('t_mult', 0),
                ability.get('x_mult', 1),
                ability.get('mult', 0)
            ]
            
            card_features = [suit_encoding, value_encoding, nominal] + ability_features
            features.extend(card_features)
        
        # Pad or truncate to fixed size (e.g., 8 cards max * 7 features each)
        max_cards = 8
        features_per_card = 7
        
        if len(features) < max_cards * features_per_card:
            features.extend([0] * (max_cards * features_per_card - len(features)))
        else:
            features = features[:max_cards * features_per_card]
        
        return np.array(features, dtype=np.float32)
    
    def _extract_game_features(self, state: Dict[str, Any]) -> np.ndarray:
        """Extract game-level features"""
        # TODO: Extract features like:
        # - Current chips
        # - Target chips
        # - Money
        # - Round/ante
        # - Discards remaining
        # - Hands remaining
        
        features = [
            state.get('state', 0),  # Game state
            len(state.get('available_actions', [])),  # Number of available actions
        ]
        
        return np.array(features, dtype=np.float32)
    
    def _encode_suit(self, suit: str) -> int:
        """Encode suit as integer"""
        suit_map = {'Hearts': 0, 'Diamonds': 1, 'Clubs': 2, 'Spades': 3}
        return suit_map.get(suit, 0)
    
    def _encode_value(self, value: str) -> int:
        """Encode card value as integer"""
        if value.isdigit():
            return int(value)
        
        value_map = {
            'Jack': 11, 'Queen': 12, 'King': 13, 'Ace': 14,
            'A': 14, 'K': 13, 'Q': 12, 'J': 11
        }
        return value_map.get(value, 0)
    
    def _calculate_reward(self) -> float:
        """Calculate reward for current state"""
        # TODO: Implement reward calculation
        # This might be based on:
        # - Chips scored
        # - Blind completion
        # - Round progression
        # - Final score
        
        return 0.0