"""
Balatro RL Environment
Wraps the pipe-based communication with Balatro mod in a standard RL interface.
This acts as a translator between Balatro's JSON pipe communication and 
RL libraries that expect gym-style step()/reset() methods.
"""

import numpy as np
from typing import Dict, Any, Tuple, List, Optional
import logging
import gymnasium as gym
from gymnasium import spaces
from ..utils.debug import tprint

from ..utils.communication import BalatroPipeIO
from .reward import BalatroRewardCalculator
from ..utils.mappers import BalatroStateMapper, BalatroActionMapper


class BalatroEnv(gym.Env):
    """
    Standard RL Environment wrapper for Balatro
    
    Translates between:
    - Balatro mod's JSON pipe communication (/tmp/balatro_request, /tmp/balatro_response)
    - Standard RL interface (step, reset, observation spaces)
    
    This allows RL libraries like Stable-Baselines3 to train on Balatro
    without knowing about the underlying pipe communication system.
    """
    
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self.current_state = None
        self.prev_state = None
        self.game_over = False
        self.restart_pending = False
        
        # Initialize communication and reward systems
        self.pipe_io = BalatroPipeIO()
        self.reward_calculator = BalatroRewardCalculator()

        # Define Gymnasium spaces
        # Action Spaces; This should describe the type and shape of the action
        # Constants
        self.MAX_ACTIONS = 10 
        action_selection = np.array([self.MAX_ACTIONS])
        card_indices = np.array([2, 2, 2, 2, 2, 2, 2, 2, 2, 2]) # Handles up to 10 cards in a hand
        self.action_space = spaces.MultiDiscrete(np.concatenate([
            action_selection,
            card_indices
        ]))
        ACTION_SLICE_LAYOUT = [
            ("action_selection", 1),
            ("card_indices", 10)
        ]
        slices = self._build_action_slices(ACTION_SLICE_LAYOUT)
        
        # Observation space: This should describe the type and shape of the observation
        # Constants
        self.OBSERVATION_SIZE = 390 # you can get this value by running test_env.py. 
        self.observation_space = spaces.Box(
            low=-np.inf, # lowest bound of observation data
            high=np.inf, # highest bound of observation data
            shape=(self.OBSERVATION_SIZE,), # Adjust based on actual state size which  This is a 1D array 
            dtype=np.float32 # Data type of the numbers
        )

        # Initialize mappers
        self.state_mapper = BalatroStateMapper(observation_size=self.OBSERVATION_SIZE, max_actions=self.MAX_ACTIONS)
        self.action_mapper = BalatroActionMapper(action_slices=slices)
    
    def reset(self, seed=None, options=None): #TODO add types
        """
        Reset the environment for a new episode
        
        In Balatro context, this means starting a new run.
        Communicates with Balatro mod via pipes to initiate reset.
        
        Returns:
            Initial observation/game state
        """
        self.current_state = None
        self.prev_state = None
        self.game_over = False
        self.restart_pending = False
        
        # Reset reward tracking
        self.reward_calculator.reset()
        
        # Wait for initial request from Balatro (game start)
        initial_request = self.pipe_io.wait_for_request()
        if not initial_request:
            raise RuntimeError("Failed to receive initial request from Balatro")

        # Send dummy response to complete hand shake
        success = self.pipe_io.send_response({"action": "ready"})
        if not success:
            raise RuntimeError("Failed to complete handshake")
         
        # Process initial state for SB3
        self.current_state = initial_request
        initial_observation = self.state_mapper.process_game_state(self.current_state)
        
        return initial_observation, {}
    
    def step(self, action): #TODO add types
        """
        Take an action in the Balatro environment
        Sends action to Balatro mod via JSON pipe, waits for response,
        calculates reward, and returns standard RL step format.
        
        Args:
            action: Action dictionary (e.g., {"action": 1, "params": {...}})
            
        Returns:
            Tuple of (observation, reward, done, info) where:
            - observation: Processed game state for neural network
            - reward: Calculated reward for this step
            - done: Whether episode is finished (game over)
            - info: Additional debug information
        """
        # Store previous state for reward calculation
        self.prev_state = self.current_state

        # Send action response to Balatro mod
        response_data = self.action_mapper.process_action(rl_action=action)
        
        success = self.pipe_io.send_response(response_data)
        if not success:
            raise RuntimeError("Failed to send response to Balatro")
        
        # Wait for next request with new game state
        next_request = self.pipe_io.wait_for_request()
        if not next_request:
            # If no response, assume game ended
            self.game_over = True
            observation = self.state_mapper.process_game_state(self.current_state)
            reward = 0.0
            return observation, reward, True, False, {"timeout": True}
        
        # Update current state
        self.current_state = next_request
        
        # Process new state for SB3
        observation = self.state_mapper.process_game_state(self.current_state)
        
        # Calculate reward using expert reward calculator
        reward = self.reward_calculator.calculate_reward(
            current_state=self.current_state,
            prev_state=self.prev_state if self.prev_state else {}
        )
        
        # Check if episode is done - delay end until after restart
        game_over_flag = self.current_state.get('game_state', {}).get('game_over', 0)
        
        if game_over_flag == 1:
            if not self.restart_pending:
                # First time seeing game over - don't end episode yet, wait for restart
                self.restart_pending = True
                done = False
            else:
                # Game has restarted after game over, now end episode
                self.restart_pending = False
                done = True
        else:
            # Normal gameplay, no episode end
            done = False
            
        terminated = done
        truncated = False  # Not using time limits for now
        
        info = {
            'balatro_state': self.current_state.get('state', 0),
            'available_actions': next_request.get('available_actions', [])
        }
        # TODO have a feeling observation is not being return when we run out of actions which causes problems
        return observation, reward, terminated, truncated, info 

    def cleanup(self):
        """
        Clean up environment resources
        
        Call this when shutting down to clean up pipe communication.
        """
        self.pipe_io.cleanup()

    @staticmethod
    def _build_action_slices(layout: List[Tuple[str, int]]) -> Dict[str, slice]:
        """
        Create slices for our actions so that we can precisely extract the
        right params to send over to balatro
        
        Args:
            layout: Our ACTION_SLICE_LAYOUT that contains action name and size
        Return:
            A dictionary containing a key being our action space slice name, and  
            the slice 
        """
        slices = {}
        start = 0
        for action_name, size in layout:
            slices[action_name] = slice(start, start + size)
            start += size
        return slices
