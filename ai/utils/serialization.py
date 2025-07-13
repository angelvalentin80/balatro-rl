"""
JSON Serialization utilities for Balatro RL
Handles conversion between game state formats
"""

import json
from typing import Dict, Any, List, Optional


class GameStateSerializer:
    """Handles serialization/deserialization of game states"""
    
    @staticmethod
    def serialize_game_state(game_state: Dict[str, Any]) -> str:
        """Convert game state dict to JSON string"""
        try:
            return json.dumps(game_state, indent=2, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize game state: {e}")
    
    @staticmethod
    def deserialize_game_state(json_string: str) -> Dict[str, Any]:
        """Convert JSON string to game state dict"""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to deserialize game state: {e}")
    
    @staticmethod
    def serialize_action(action: Dict[str, Any]) -> str:
        """Convert action dict to JSON string"""
        try:
            return json.dumps(action, ensure_ascii=False)
        except (TypeError, ValueError) as e:
            raise ValueError(f"Failed to serialize action: {e}")
    
    @staticmethod
    def deserialize_action(json_string: str) -> Dict[str, Any]:
        """Convert JSON string to action dict"""
        try:
            return json.loads(json_string)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to deserialize action: {e}")


class GameStateValidator:
    """Validates game state structure and content"""
    
    @staticmethod
    def validate_game_state(game_state: Dict[str, Any]) -> bool:
        """Validate that game state has required fields"""
        required_fields = ['state', 'available_actions']
        
        for field in required_fields:
            if field not in game_state:
                raise ValueError(f"Missing required field: {field}")
        
        # Validate hand structure if present
        if 'hand' in game_state:
            GameStateValidator._validate_hand(game_state['hand'])
        
        return True
    
    @staticmethod
    def _validate_hand(hand: Dict[str, Any]) -> bool:
        """Validate hand structure"""
        if not isinstance(hand, dict):
            raise ValueError("Hand must be a dictionary")
        
        if 'cards' in hand and not isinstance(hand['cards'], list):
            raise ValueError("Hand cards must be a list")
        
        # Validate each card
        for i, card in enumerate(hand.get('cards', [])):
            GameStateValidator._validate_card(card, i)
        
        return True
    
    @staticmethod
    def _validate_card(card: Dict[str, Any], index: int) -> bool:
        """Validate individual card structure"""
        required_fields = ['suit', 'base']
        
        for field in required_fields:
            if field not in card:
                raise ValueError(f"Card {index} missing required field: {field}")
        
        # Validate base structure
        if 'base' in card:
            base = card['base']
            if 'value' not in base or 'nominal' not in base:
                raise ValueError(f"Card {index} base missing value or nominal")
        
        return True
    
    @staticmethod
    def validate_action(action: Dict[str, Any]) -> bool:
        """Validate action structure"""
        if 'action' not in action:
            raise ValueError("Action must have 'action' field")
        
        action_type = action['action']
        
        # Validate specific action types
        if action_type in ['play_hand', 'discard']:
            if 'card_indices' not in action:
                raise ValueError(f"Action {action_type} requires card_indices")
            
            if not isinstance(action['card_indices'], list):
                raise ValueError("card_indices must be a list")
        
        return True


# Convenience functions
def to_json(obj: Dict[str, Any]) -> str:
    """Quick serialize to JSON"""
    return GameStateSerializer.serialize_game_state(obj)

def from_json(json_str: str) -> Dict[str, Any]:
    """Quick deserialize from JSON"""  
    return GameStateSerializer.deserialize_game_state(json_str)