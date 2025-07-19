"""
Game State Validation utilities for Balatro RL
Validates game state structure and content
"""

from typing import Dict, Any, List



class GameStateValidator:
    """
    Validates game state json structure

    Request Contract (Macro level not everything)
    {
        game_state: Dict, # The whole game state table 
        available_actions: List, # The available actions all as integers
        retry_count: int, # TODO update observation space. this is to handle retries if AI fails
    }
    """
    
    @staticmethod
    def validate_game_state(game_state: Dict[str, Any]) -> bool:
        """Validate that game state has required fields"""
        required_fields = ['game_state', 'available_actions', 'retry_count']
        # TODO we can add more validations as needed like ensuring available_actions is a list and stuff
        # TODO game_over might be a validation
        # TODO validate chips for rewards
        
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

class ResponseValidator:
    """
    Validates response json structure

    Response contract 
    {
        action, # The action to take
        params, # The params in the event the action takes in params
    }
    """

    @staticmethod
    def validate_response(response: Dict[str, Any]):
        required_fields = ["action"]
        for field in required_fields:
            if field not in response:
                raise ValueError(f"Missing required field: {field}")

