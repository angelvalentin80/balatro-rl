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

from ..utils.communication import BalatroPipeIO
from .reward import BalatroRewardCalculator
from ..utils.mappers import BalatroStateMapper, BalatroActionMapper
from ..utils.replay import ReplaySystem


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

        # Replay System
        self.replay_system = ReplaySystem()
        self.actions_taken = []

        # Define Gymnasium spaces
        # Action Spaces; This should describe the type and shape of the action
        # Constants - Core gameplay actions only (SELECT_HAND=1, PLAY_HAND=2, DISCARD_HAND=3)
        self.MAX_ACTIONS = 3
        self.MAX_CARDS = 8  # Max cards in hand
        action_selection = np.array([self.MAX_ACTIONS])
        card_indices = np.array([2] * self.MAX_CARDS) # 8 cards, each can be selected (1) or not (0) #TODO can we or have we already masked card selection?
        self.action_space = spaces.MultiDiscrete(np.concatenate([
            action_selection,
            card_indices
        ]))
        ACTION_SLICE_LAYOUT = [
            ("action_selection", 1),
            ("card_indices", self.MAX_CARDS)
        ]
        slices = self._build_action_slices(ACTION_SLICE_LAYOUT)
        
        # Observation space: This should describe the type and shape of the observation
        # Constants
        self.OBSERVATION_SIZE = 216
        self.observation_space = spaces.Box(
            low=-np.inf, # lowest bound of observation data
            high=np.inf, # highest bound of observation data
            shape=(self.OBSERVATION_SIZE,), # Adjust based on actual state size which  This is a 1D array 
            dtype=np.float32 # Data type of the numbers
        )

        # Initialize mappers
        self.state_mapper = BalatroStateMapper(observation_size=self.OBSERVATION_SIZE, max_actions=self.MAX_ACTIONS)
        self.action_mapper = BalatroActionMapper(action_slices=slices)
    
    def reset(self, seed=None, options=None):
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
        self.actions_taken = []
        
        # Reset reward tracking
        self.reward_calculator.reset()
        
        # Wait for initial request from Balatro (game start)
        initial_request = self.pipe_io.wait_for_request()
        if not initial_request:
            raise RuntimeError("Failed to receive initial request from Balatro")

        # Process initial state for SB3
        self.current_state = initial_request
        initial_observation = self.state_mapper.process_game_state(self.current_state)
        
        # Create initial action mask
        initial_available_actions = initial_request.get('available_actions', [])
        initial_action_mask = self._create_action_mask(initial_available_actions)
        self._action_masks = initial_action_mask
        
        return initial_observation, {}
    
    def step(self, action):
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
        self.actions_taken.append(response_data)
        success = self.pipe_io.send_response(response_data)
        if not success:
            raise RuntimeError("Failed to send response to Balatro")
        
        # Wait for next request with new game state
        next_request = self.pipe_io.wait_for_request()
        if not next_request:
            self.game_over = True
            observation = self.state_mapper.process_game_state(self.current_state)
            reward = 0.0
            return observation, reward, True, False, {"timeout": True}
        
        # Update current state
        self.current_state = next_request
        game_state = self.current_state.get('game_state', {})
        
        # Check for game over condition
        game_over_flag = game_state.get('game_over', 0)
        if game_over_flag == 1:
            observation = self.state_mapper.process_game_state(self.current_state)
            reward = self.reward_calculator.calculate_reward(
                current_state=self.current_state,
                prev_state=self.prev_state if self.prev_state else {}
            )
            
            # Auto-send restart command to Balatro
            restart_response = {"action": 6, "params": []}
            self.pipe_io.send_response(restart_response)
            
            return observation, reward, True, False, {}

        # Check for game win condition
        game_win_flag = game_state.get('game_win', 0)
        if game_win_flag == 1:
            observation = self.state_mapper.process_game_state(self.current_state)
            reward = self.reward_calculator.calculate_reward(
                current_state=self.current_state,
                prev_state=self.prev_state if self.prev_state else {}
            )

            # Save replay
            self.replay_system.try_save_replay(
                file_path=self.replay_system.REPLAY_FILE_PATH,
                seed=game_state.get('seed', ''),
                actions=self.actions_taken,
                score=reward,
                chips=game_state.get('chips', 0)
            )
            
            # Auto-send restart command to Balatro
            restart_response = {"action": 6, "params": []}
            self.pipe_io.send_response(restart_response)
            
            return observation, reward, True, False, {}


        # Process new state for SB3
        observation = self.state_mapper.process_game_state(self.current_state)
        
        # Calculate reward using expert reward calculator
        reward = self.reward_calculator.calculate_reward(
            current_state=self.current_state,
            prev_state=self.prev_state if self.prev_state else {}
        )
        
        done = False
            
        terminated = done
        truncated = False  # Not using time limits for now
        
        # Create action mask for MaskablePPO
        available_actions = next_request.get('available_actions', [])
        action_mask = self._create_action_mask(available_actions)
        
        info = {}
        
        # Store action mask for MaskablePPO
        self._action_masks = action_mask
        
        return observation, reward, terminated, truncated, info

    def cleanup(self):
        """
        Clean up environment resources
        
        Call this when shutting down to clean up pipe communication.
        """
        self.pipe_io.cleanup()

    # Action Masks for MaskablePPO and for ActionWrapper
    def action_masks(self):
        """Required method for MaskablePPO"""
        if hasattr(self, '_action_masks'):
            return np.array(self._action_masks, dtype=bool)
        else:
            return np.array([True] * sum(self.action_space.nvec), dtype=bool)
    
    def _create_action_mask(self, available_actions):
        """Create action mask for MultiDiscrete space"""
        action_masks = []
        
        # Action selection mask (3 possible actions: SELECT_HAND=1, PLAY_HAND=2, DISCARD_HAND=3)
        # Map Balatro action IDs to AI indices: 1->0, 2->1, 3->2
        action_selection_mask = [False] * self.MAX_ACTIONS
        balatro_to_ai_mapping = {1: 0, 2: 1, 3: 2}  # SELECT_HAND, PLAY_HAND, DISCARD_HAND
        
        for action_id in available_actions:
            if action_id in balatro_to_ai_mapping:
                ai_index = balatro_to_ai_mapping[action_id]
                action_selection_mask[ai_index] = True
        action_masks.append(action_selection_mask)
        
        # Card selection masks - context-aware based on available actions
        if any(action_id in [2, 3] for action_id in available_actions):
            # PLAY_HAND or DISCARD_HAND available - card params don't matter
            for _ in range(self.MAX_CARDS):
                action_masks.append([True, False])  # Force "not selected"
        else:
            # Only SELECT_HAND available - allow card selection
            for _ in range(self.MAX_CARDS):
                action_masks.append([True, True])
        
        # Flatten for MaskablePPO
        return [item for sublist in action_masks for item in sublist] 

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
