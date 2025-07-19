"""
Environment Testing Script for Balatro RL

Tests the BalatroEnv to ensure it follows the Gym interface and 
communicates properly with the Balatro mod via file I/O.

Usage:
    python test_env.py
"""

import time
import logging
# from stable_baselines3.common.env_checker import check_env  # Not compatible with pipes
from .environment.balatro_env import BalatroEnv


def test_manual_actions():
    """Manual testing with random actions"""
    print("\n=== Manual Action Testing ===")
    
    env = BalatroEnv()
    print("BalatroEnv created successfully")
    
    try:
        # Reset and get initial observation (ONLY ONCE!)
        print("Calling env.reset() - this should wait for Balatro...")
        obs, info = env.reset()
        print("env.reset() completed!")
        print(f"Initial observation: {obs}")
        print(f"Observation space: {env.observation_space}")
        print(f"Action space: {env.action_space}")
        print(f"Sample action: {env.action_space.sample()}")
        
        # Run test episodes
        max_steps = 3 
        max_episodes = 1 
        
        for episode in range(max_episodes):
            print(f"\n--- Episode {episode + 1} ---")
            # Don't call reset() again! Use the obs from above
            
            for step in range(max_steps):
                # Get random action (like the old balatro_agent)
                action = env.action_space.sample()
                
                print(f"Step {step + 1}: Taking action {action}")
                
                # Take action
                obs, reward, terminated, truncated, info = env.step(action)
                done = terminated or truncated
                
                print(f"  obs={obs}, reward={reward}, done={done}")
                
                # Optional: Add delay for readability
                time.sleep(0.1)
                
                if done:
                    print(f"  Episode finished after {step + 1} steps")
                    break
            
            if not done:
                print(f"  Episode reached max steps ({max_steps})")
                
    except Exception as e:
        print(f"✗ Manual testing failed: {e}")
        return False
    finally:
        env.close() 
    
    print("✓ Manual testing completed!")
    return True


def main():
    """Run all tests"""
    print("Starting Balatro Environment Testing...")
    
    # Setup logging to see communication details
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    success = True
    success &= test_manual_actions()
    
    if success:
        print("\n🎉 All tests passed! Environment is ready for training.")
    else:
        print("\n❌ Some tests failed. Check the environment implementation.")
    
    return success


if __name__ == "__main__":
    main()
