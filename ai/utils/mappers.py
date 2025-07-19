"""
Mappers for converting between Balatro game data and RL-compatible formats.

This module handles the two-way data transformation:
1. BalatroStateMapper: Converts incoming Balatro JSON to normalized RL observations
2. BalatroActionMapper: Converts RL actions to Balatro command JSON
"""

import numpy as np
import time
from typing import Dict, List, Any
from ..utils.validation import GameStateValidator, ResponseValidator
import logging



class BalatroStateMapper:
    """
    Converts raw Balatro game state JSON to normalized RL observations.
    
    Handles:
    - Card data normalization
    - Game state parsing
    - Observation space formatting
    """
    def __init__(self, observation_size: int, max_actions: int):
        self.observation_size = observation_size
        self.max_actions = max_actions

        # Logger
        self.logger = logging.getLogger(__name__)

        # GameStateValidator
        self.game_state_validator = GameStateValidator()

    #TODO review Might be something wrong here
    def process_game_state(self, raw_state: Dict[str, Any] | None) -> np.ndarray:
        """
        Convert Balatro's raw JSON game state into neural network input format
        converting into standardized numerical arrays that neural networks can 
        process.
        
        Args:
            raw_state: Raw game state from Balatro mod JSON
            
        Returns:
            Processed state suitable for RL training
        """
        if not raw_state:
            return np.zeros(self.observation_size, dtype=np.float32) # TODO maybe raise error?
        
        # Validate game state request 
        try:
            self.game_state_validator.validate_game_state(raw_state)
        except ValueError as e:
            self.logger.error(f"Invalid game state: {e}")
        
        hand_features = self._extract_hand_features(raw_state.get('hand', {}))
        game_features = self._extract_game_features(raw_state)
        available_actions = self._extract_available_actions(raw_state.get('available_actions', []))
        chips = self._extract_chip_features(raw_state)
        # TODO extract state
        
        return np.concatenate([hand_features, game_features, available_actions, chips])
    
    def _extract_available_actions(self, available_actions: List[int]) -> np.ndarray:
        """
        Convert available actions into a np array
        Args:
            available_actions: Available actions list from Balatro game state
        Returns:
            Fixed-size numpy array of hand features
        """
        mask = np.zeros(self.max_actions, dtype=np.float32)
        for action_id in available_actions:
            mask[action_id] = 1.0
        return mask
    
    def _extract_hand_features(self, hand: Dict[str, Any]) -> np.ndarray:
        """
        Convert Balatro hand data into numerical features for neural network
        
        Transforms card dictionaries into fixed-size numerical arrays:
        - Card values: 2-14 (2 through Ace)
        - Suits: 0-3 (Hearts, Diamonds, Clubs, Spades)
        - Card abilities: chips, mult, special effects
        - Pads/truncates to fixed hand size for consistent input
        
        Args:
            hand: Hand dictionary from Balatro game state
            
        Returns:
            Fixed-size numpy array of hand features
        """
        
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
        # TODO hand.get('size')
        # TODO hand.get('highlighted_count')
        max_cards = 8
        features_per_card = 7
        
        if len(features) < max_cards * features_per_card:
            features.extend([0] * (max_cards * features_per_card - len(features)))
        else:
            features = features[:max_cards * features_per_card]
        
        return np.array(features, dtype=np.float32)
    
    def _extract_game_features(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Extract numerical game-level features from Balatro state
        
        Converts game metadata into neural network inputs:
        - Current game state (menu, selecting hand, etc.)
        - Available actions count
        - Money, chips, round progression
        - Remaining hands/discards
        
        Args:
            state: Full Balatro game state dictionary
            
        Returns:
            Numpy array of normalized game features
        """
        
        features = [
            state.get('state', 0),  # Game state
            len(state.get('available_actions', [])),  # Number of available actions
        ]
        
        return np.array(features, dtype=np.float32)
    
    def _extract_chip_features(self, state: Dict[str, Any]) -> np.ndarray:
        """
        Extract information relating to chips

        Args:
            state: Full Balatro game state dictionary
        Returns:
            Numpy array of normalized chip features
        """
        features = [
            state.get('chips', 0),
            state.get('chip_target', 0)
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



class BalatroActionMapper:
    """
    Converts RL actions to Balatro command JSON.
    
    Handles:
    - Binary action conversion to card indices
    - Action validation
    - JSON response formatting
    """
    
    def __init__(self, action_slices: Dict[str, slice]):
        self.slices = action_slices

        # Validator
        self.response_validator = ResponseValidator()

        # Logger
        self.logger = logging.getLogger(__name__)

    def process_action(self, rl_action: np.ndarray) -> Dict[str, Any]:
        """
        Convert RL action to Balatro JSON.
        
        Args:
            rl_action: Binary action array from RL agent
            game_state: Current game state for validation
            
        Returns:
            JSON response formatted for Balatro mod
        """
        ai_action = rl_action[self.slices["action_selection"]].tolist()[0]
        response_data = {
            "action": ai_action,
            "params": self._extract_select_hand_params(rl_action),
        }
        self.response_validator.validate_response(response_data)

        # Validate action structure
        try:
            self.response_validator.validate_response(response_data)
        except ValueError as e:
            self.logger.error(f"Invalid game state: {e}")

        return response_data

    def _extract_select_hand_params(self, raw_action: np.ndarray) -> List[int]:
        """
        Converts the raw action to a list of Lua card indices

        Args:
            raw_action: The whole action from the RL agent
        Returns:
            List of 1-based card indices for Lua
        """
        card_indices = raw_action[self.slices["card_indices"]]
        return [i + 1 for i, val in enumerate(card_indices) if val == 1]


