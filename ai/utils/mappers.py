"""
Mappers for converting between Balatro game data and RL-compatible formats.

This module handles the two-way data transformation:
1. BalatroStateMapper: Converts incoming Balatro JSON to normalized RL observations
2. BalatroActionMapper: Converts RL actions to Balatro command JSON
"""

import numpy as np
from typing import Dict, List, Any
from ..utils.validation import GameStateValidator, ResponseValidator
import logging


def make_onehot(value: int, num_classes: int) -> List[float]:
    """
    Create one-hot encoding for categorical values.
    
    Args:
        value: The category index (0-based)
        num_classes: Total number of possible categories
        
    Returns:
        One-hot encoded list where only the value position is 1.0
        
    Example:
        make_onehot(2, 5) -> [0.0, 0.0, 1.0, 0.0, 0.0]
    """
    onehot = [0.0] * num_classes
    if 0 <= value < num_classes:
        onehot[value] = 1.0
    return onehot


def make_mask(available_items: List[int], total_slots: int) -> List[float]:
    """
    Create binary mask for available items/actions.
    
    Args:
        available_items: List of available indices
        total_slots: Total number of possible slots
        
    Returns:
        Binary mask where available positions are 1.0
        
    Example:
        make_mask([1, 3, 5], 6) -> [0.0, 1.0, 0.0, 1.0, 0.0, 1.0]
    """
    mask = [0.0] * total_slots
    for item in available_items:
        if 0 <= item < total_slots:
            mask[item] = 1.0
    return mask


def normalize(value: float, max_value: float) -> float:
    """
    Normalize a value to 0-1 range.
    
    Args:
        value: Value to normalize
        max_value: Maximum possible value for scaling
        
    Returns:
        Normalized value between 0.0 and 1.0
        
    Example:
        normalize(1500, 3000) -> 0.5  # Halfway to max
        normalize(50, 100) -> 0.5     # Also halfway
    """
    return value / max_value if max_value > 0 else 0.0



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

    def process_game_state(self, raw_state: Dict[str, Any] | None) -> np.ndarray:
        """
        Convert Balatro's raw JSON game state into neural network input format
        converting into standardized numerical arrays that neural networks can 
        process.
        
        Args:
            raw_state: Raw game state from Balatro mod JSON
            
        Returns:
            Processed numpy array state suitable for RL training
        """
        # Handle gracefully 
        if not raw_state:
            return np.zeros(self.observation_size, dtype=np.float32)
        
        # Validate game state request 
        try:
            self.game_state_validator.validate_game_state(raw_state)
        except ValueError as e:
            self.logger.error(f"Invalid game state: {e}")

        features = []
        
        features.extend(self._extract_game_features(raw_state.get('game_state', {})))
        features.extend(self._extract_available_actions(raw_state.get('available_actions', [])))

        return np.array(features, dtype=np.float32)
    
    def _extract_available_actions(self, available_actions: List[int]) -> List[float]:
        """
        Convert available actions into a fixed-size mask
        Args:
            available_actions: Available actions list from Balatro game state
        Returns:
            Fixed-size list of available action features
        """
        return make_mask(available_actions, self.max_actions)
    
    def _extract_hand_features(self, hand: Dict[str, Any]) -> List[float]:
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
            Fixed-size list of hand features
        """
        features = []
        
        cards = hand.get('cards', [])

        NON_CARDS_FEATURES = 2 # TODO Update this if we add more non-card features
        features.append(float(hand.get('size', 0)))
        features.append(float(hand.get('highlighted_count', 0)))
        
        
        for card in cards:
            card_features = []
            card_features.append(float(card.get('highlighted', False)))
            
            # Suit one-hot
            suits_mapping = {"Hearts": 0, "Diamonds": 1, "Spades": 2, "Clubs": 3}
            suit = card.get('suit', 'Unknown')
            card_features.extend(make_onehot(suits_mapping.get(suit, 4), 5))
            
            # Card value one-hot
            base = card.get('base', {})
            values_mapping = {
                '2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, '10': 8,
                'Jack': 9, 'Queen': 10, 'King': 11, 'Ace': 12
            }
            value = base.get('value')
            card_features.extend(make_onehot(values_mapping.get(value, 13), 14))
            
            # Nominal value (actual chip value used in game calculations)
            card_features.append(base.get('nominal', 0.0))

            features.extend(card_features)
        
        # Pad or truncate to fixed size 
        max_cards = 8  # TODO this might have to be updated in future if we go bigger Standard Balatro hand size
        features_per_card = 21  # 1+5+14+1 = highlighted+suit_onehot+value_onehot+nominal
        
        # If no cards in hand, pad with zeros
        if len(features) == NON_CARDS_FEATURES:
            features.extend([0.0] * (max_cards * features_per_card))
        
        return features
    
    def _extract_game_features(self, state: Dict[str, Any]) -> List[float]:
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
            List of normalized game features
        """
        features = []
        features.extend(self._extract_round_features(state.get('round', {})))
        features.append(float(state.get('blind_chips', 0)))
        features.append(float(state.get('chips', 0)))
        features.extend(make_onehot(state.get('state', 0), 20))
        features.append(float(state.get('game_over', 0)))
        features.append(float(state.get('retry_count', 0)))
        features.extend(self._extract_hand_features(state.get('hand', {})))
        features.extend(self._extract_current_hand_scoring(state.get('current_hand', {})))

        return features

    
    def _extract_round_features(self, round: Dict[str, Any]) -> List[float]:
        """
        Extract information relating to rounds 
        
        Args:
            round: Round state inside of the game_state dictionary
        Returns:
            List of round features
        """
        features = []
        features.append(float(round.get('hands_left', 0)))
        features.append(float(round.get('discards_left', 0)))
        return features



    def _extract_current_hand_scoring(self, current_hand: Dict[str, Any]) -> List[float]:
        """
        Extract current hand scoring information (chips, mult, score, hand type)
        
        Args:
            current_hand: Current hand scoring data from game state
            
        Returns:
            List with chips, mult, score, and one-hot encoded hand type (16 dimensions total)
        """
        features = []
        
        # Raw scoring values
        features.append(float(current_hand.get('chips', 0)))
        features.append(float(current_hand.get('mult', 0)))  
        features.append(float(current_hand.get('score', 0)))
        
        # Hand type one-hot encoding
        hand_types = [
            "None",          # 0 - No hand played yet
            "High Card",     # 1
            "Pair",          # 2
            "Two Pair",      # 3
            "Three of a Kind", # 4
            "Straight",      # 5
            "Flush",         # 6
            "Full House",    # 7
            "Four of a Kind", # 8
            "Straight Flush", # 9
            "Five of a Kind", # 10
            "Flush House",   # 11
            "Flush Five"     # 12
        ]
        
        hand_name = current_hand.get('handname', 'None')
        if not hand_name:
            hand_name = "None"
        hand_index = hand_types.index(hand_name)

        features.extend(make_onehot(hand_index, len(hand_types)))
        
        return features
    
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
        
        # Map AI indices to Balatro action IDs: 0->1, 1->2, 2->3
        ai_to_balatro_mapping = {0: 1, 1: 2, 2: 3}  # SELECT_HAND, PLAY_HAND, DISCARD_HAND
        balatro_action_id = ai_to_balatro_mapping.get(ai_action, 1)  # Default to SELECT_HAND
        
        response_data = {
            "action": balatro_action_id,
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


