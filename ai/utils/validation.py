"""
Game State Validation utilities for Balatro RL
Validates game state structure and content
"""

from typing import Dict, Any, List

from numpy import inner



class GameStateValidator:
    """
    Validates game state json structure

    Request Contract (Macro level not everything)
    {
        game_state: Dict, # The whole game state table 
        available_actions: List, # The available actions all as integers
    }
    """
    
    @staticmethod
    def validate_game_state(game_state: Dict[str, Any]) -> bool:
        """Validate that game state has required fields"""
        required_fields = ['game_state', 'available_actions']
        
        for field in required_fields:
            assert field in game_state, f"Missing required field: {field}"

        # Validate
        inner_game_state = game_state.get("game_state")
        assert isinstance(inner_game_state, dict), "game_state must be a dictionary"
        available_actions = game_state.get("available_actions")
        assert isinstance(available_actions, list), "available_actions must be a list"

        GameStateValidator._validate_inner_game_state(inner_game_state)
        
        return True

    @staticmethod
    def _validate_inner_game_state(game_state: Dict[str, Any]) -> bool:
        """
        Validate the inner game state fields. We call it inner game state because
        this is the actual game loop in the game, meanwhile normal game_state
        deals with things outside of the game like whether we are in the main menu
        etc
        """
        # Conditional validations in game_state
        GameStateValidator._validate_hand(game_state['hand'])
        GameStateValidator._validate_round(game_state['round'])
        GameStateValidator._validate_current_hand(game_state['current_hand'])
        assert game_state["game_over"] in [0, 1]
        assert isinstance(game_state["state"], int)
        assert isinstance(game_state["blind_chips"], (int, float))
        assert isinstance(game_state["chips"], (int, float))

        return True

    @staticmethod
    def _validate_current_hand(current_hand: Dict[str, Any]) -> bool:
        """Validate current hand scoring structure"""
        required_fields = ["chips", "mult", "score", "handname"]
        for field in required_fields:
            assert field in current_hand, f"Missing required field: {field}"
        assert isinstance(current_hand["handname"], str)
        return True

    @staticmethod
    def _validate_round(round: Dict[str, Any]) -> bool:
        """Validate round structure"""
        required_fields = ["hands_left", "discards_left"]
        for field in required_fields:
            assert field in round, f"Missing required field: {field}"
        return True


    @staticmethod
    def _validate_hand(hand: Dict[str, Any]) -> bool:
        """Validate hand structure"""
        required_fields = ["size", "cards", "highlighted_count"]
        for field in required_fields:
            assert field in hand, f"Missing required field: {field}"

        if not isinstance(hand['cards'], list):
            raise ValueError("Hand cards must be a list")
        
        # Validate each card
        for i, card in enumerate(hand.get('cards', [])):
            GameStateValidator._validate_card(card, i)
        
        return True
    
    @staticmethod
    def _validate_card(card: Dict[str, Any], index: int) -> bool:
        """Validate individual card structure"""
        required_fields = ['suit', 'base', 'highlighted', 'debuff']
        
        for field in required_fields:
            assert field in card, f"Card {index} missing required field: {field}"
        
        # Validate base structure
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
        required_fields = ["action", "params"]
        for field in required_fields:
            assert field in response, f"Missing required field: {field}"

        assert isinstance(response["action"], int)
        assert isinstance(response["params"], list)

