"""
Balatro RL Agent
Contains the AI logic for making decisions in Balatro
"""

from typing import Dict, Any, List
import random
import logging


class BalatroAgent:
    """Main AI agent for playing Balatro"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # TODO: Initialize your RL model here
        # self.model = load_model("path/to/model")
        # self.training = True
        
    def get_action(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Given game state, return the action to take
        
        Args:
            game_state: Current game state from Balatro mod
            
        Returns:
            Action dictionary to send back to mod
        """
        try:
            # Extract relevant info from game state
            available_actions = request.get('available_actions', [])
            game_state = request.get('game_state', {})
            
            self.logger.info(f"Processing state {game_state.get('state', 0)} with {len(available_actions)} actions")
            
            # TODO: Replace with actual RL logic
            action = self._get_random_action(available_actions) # TODO we are getting random actions for testing
            
            # TODO: If training, update model with reward
            # if self.training:
            #     self._update_model(game_state, action, reward)
            
            return action
            
        except Exception as e:
            self.logger.error(f"Error in get_action: {e}")
            return {"action": "no_action"}
    
    def _get_random_action(self, available_actions: List) -> Dict[str, Any]:
        """Temporary random action selection - replace with RL logic"""
        
        # available_actions comes as [1, 2] format
        if not available_actions or not isinstance(available_actions, List):
            return {"action": "no_action"}
                
        # Simple random action selection  
        selected_action_id = random.choice(available_actions)
        self.logger.info(f"Selected action ID: {selected_action_id} from available: {available_actions}")
        
        # TODO this is for testing, the AI doesn't really care about what the action_names are
        # but we do so we can test out actions and make sure they work
        # Map action IDs to names for logic (but return the ID)
        action_names = {1: "start_run", 2: "select_blind", 3: "select_hand"}
        action_name = action_names.get(selected_action_id, "unknown")
        
        # Pick random cards for now
        params = {}
        if action_name == "select_hand":
            params["card_indices"] = [1, 3, 5]
        
        # Return the action ID (number), not the name
        return {"action": selected_action_id, "params": params}
    
    def train_step(self, game_state: Dict, action: Dict, reward: float, next_state: Dict):
        """
        Perform one training step
        
        TODO: Implement RL training logic here
        - Update Q-values
        - Update neural network weights
        - Store experience in replay buffer
        """
        pass
    
    def save_model(self, path: str):
        """Save the trained model"""
        # TODO: Implement model saving
        pass
    
    def load_model(self, path: str):
        """Load a trained model"""
        # TODO: Implement model loading
        pass
