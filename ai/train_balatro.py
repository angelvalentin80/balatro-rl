#!/usr/bin/env python3
"""
Balatro RL Training Script

Main training script for teaching AI to play Balatro using Stable-Baselines3.
This script creates the Balatro environment, sets up the RL model, and runs training.

Usage:
    python train_balatro.py

Requirements:
    - Balatro game running with RLBridge mod
    - file_watcher.py should NOT be running (this replaces it)
"""

import logging
import time
from pathlib import Path

# SB3 imports
from stable_baselines3 import DQN, A2C, PPO
from stable_baselines3.common.callbacks import EvalCallback, CheckpointCallback
from stable_baselines3.common.monitor import Monitor

# Our custom environment
from .environment.balatro_env import BalatroEnv


def setup_logging():
    """Setup logging for training"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('training.log'),
            logging.StreamHandler()
        ]
    )


def create_environment():
    """Create and wrap the Balatro environment"""
    # Create base environment
    env = BalatroEnv()
    
    # Wrap with Monitor for logging episode stats
    env = Monitor(env, filename="training_monitor.csv")
    
    return env


def create_model(env, algorithm="DQN", model_path=None):
    """
    Create SB3 model for training
    
    Args:
        env: Balatro environment
        algorithm: RL algorithm to use ("DQN", "A2C", "PPO")
        model_path: Path to load existing model (optional)
    
    Returns:
        SB3 model ready for training
    """
    if algorithm == "DQN":
        model = DQN(
            "MlpPolicy", 
            env, 
            verbose=1,
            learning_rate=1e-4,
            buffer_size=10000,
            learning_starts=1000,
            target_update_interval=500,
            train_freq=4,
            gradient_steps=1,
            exploration_fraction=0.1,
            exploration_initial_eps=1.0,
            exploration_final_eps=0.05,
            tensorboard_log="./tensorboard_logs/"
        )
    elif algorithm == "A2C":
        model = A2C(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=7e-4,
            n_steps=5,
            gamma=0.99,
            tensorboard_log="./tensorboard_logs/"
        )
    elif algorithm == "PPO":
        model = PPO(
            "MlpPolicy",
            env,
            verbose=1,
            learning_rate=3e-4,
            n_steps=2048,
            batch_size=64,
            n_epochs=10,
            gamma=0.99,
            tensorboard_log="./tensorboard_logs/"
        )
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")
    
    # Load existing model if path provided
    if model_path and Path(model_path).exists():
        model.load(model_path)
        print(f"Loaded existing model from {model_path}")
    
    return model


def create_callbacks(save_freq=1000):
    """Create training callbacks for saving and evaluation"""
    callbacks = []
    
    # Checkpoint callback - save model periodically
    checkpoint_callback = CheckpointCallback(
        save_freq=save_freq,
        save_path="./models/",
        name_prefix="balatro_model"
    )
    callbacks.append(checkpoint_callback)
    
    return callbacks


def train_agent(total_timesteps=50000, algorithm="DQN", save_path="./models/balatro_final"):
    """
    Main training function
    
    Args:
        total_timesteps: Number of training steps
        algorithm: RL algorithm to use
        save_path: Where to save final model
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Starting Balatro RL training with {algorithm}")
    logger.info(f"Training for {total_timesteps} timesteps")
    
    try:
        # Create environment and model
        env = create_environment()
        model = create_model(env, algorithm)
        
        # Create callbacks
        callbacks = create_callbacks(save_freq=max(1000, total_timesteps // 20))
        
        # Train the model
        logger.info("Starting training...")
        start_time = time.time()
        
        model.learn(
            total_timesteps=total_timesteps,
            callback=callbacks,
            progress_bar=True
        )
        
        training_time = time.time() - start_time
        logger.info(f"Training completed in {training_time:.2f} seconds")
        
        # Save final model
        model.save(save_path)
        logger.info(f"Model saved to {save_path}")
        
        # Clean up environment  
        if hasattr(env, 'cleanup'):
            env.cleanup()
        elif hasattr(env.env, 'cleanup'):  # Monitor wrapper
            env.env.cleanup()
        
        return model
        
    except KeyboardInterrupt:
        logger.info("Training interrupted by user")
        if hasattr(env, 'cleanup'):
            env.cleanup()
        elif hasattr(env.env, 'cleanup'):
            env.env.cleanup()
        return None
    except Exception as e:
        logger.error(f"Training failed: {e}")
        if hasattr(env, 'cleanup'):
            env.cleanup()
        elif hasattr(env.env, 'cleanup'):
            env.env.cleanup()
        raise


def test_trained_model(model_path, num_episodes=5):
    """
    Test a trained model
    
    Args:
        model_path: Path to trained model
        num_episodes: Number of episodes to test
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Testing model from {model_path}")
    
    # Create environment and load model
    env = create_environment()
    model = DQN.load(model_path)
    
    episode_rewards = []
    
    for episode in range(num_episodes):
        obs = env.reset()
        total_reward = 0
        steps = 0
        
        while True:
            action, _states = model.predict(obs, deterministic=True)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            steps += 1
            
            if done:
                break
        
        episode_rewards.append(total_reward)
        logger.info(f"Episode {episode + 1}: {steps} steps, reward: {total_reward:.2f}")
    
    avg_reward = sum(episode_rewards) / len(episode_rewards)
    logger.info(f"Average reward over {num_episodes} episodes: {avg_reward:.2f}")
    
    env.cleanup()
    return episode_rewards


if __name__ == "__main__":
    # Setup
    setup_logging()
    
    # Create necessary directories
    Path(".models").mkdir(exist_ok=True)
    Path(".tensorboard_logs").mkdir(exist_ok=True)
    
    # We'll let BalatroEnv create the pipes when needed
    print("🔧 Pipe communication will be initialized with environment...")
    
    # Train the agent
    print("\n🎮 Starting Balatro RL Training!")
    print("Setup steps:")
    print("1. ✅ Balatro is running with RLBridge mod")
    print("2. ✅ Balatro is in menu state")
    print("3. Press Enter below to start training")
    print("4. When prompted, press 'R' in Balatro within 3 seconds")
    print("\n📡 Training will create pipes and connect automatically!")
    print()
    
    input("Press Enter to start training (then you'll have 3 seconds to press 'R' in Balatro)...")
    
    try:
        model = train_agent(
            total_timesteps=10000,  # Start small for testing
            algorithm="PPO",  # PPO supports MultiDiscrete actions
            save_path="./models/balatro_trained"
        )
        
        if model:
            print("\n🎉 Training completed successfully!")
            print("Testing the trained model...")
            
            # Test the trained model
            test_trained_model("./models/balatro_trained", num_episodes=3)
            
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print("Check the logs for more details.")
    finally:
        # Pipes will be cleaned up by the environment
        print("🧹 Training session ended")
