# Balatro RL

A reinforcement learning agent that plays Balatro using a custom mod and Python training environment.

## Overview

This project combines a Balatro mod (RLBridge) with a Python reinforcement learning environment to train an AI agent to play Balatro. The mod extracts game state information and executes actions from the RL agent via a dual-pipe communication system.

## Features

- **Game State Extraction**: Reads hand cards, chips, available hands/discards, and other game state data
- **Action Execution**: AI can play hands, discard cards, select hands
- **Dual-pipe Communication**: Request/response system using named pipes for real-time communication
- **Replay System**: Automatically saves winning games with top 10 highest chip score 
- **Custom Reward Function**: Rewards efficient play, complex hands, and winning rounds
- **Automated Training**: Runs automatically start new games after wins/losses

## Installation

### Prerequisites
- Balatro (Steam version)
- [Lovely Injector](https://github.com/ethangreen-dev/lovely-injector) for mod injection
- Python 3.8+ with dependencies (requirements.txt)

### Setup
1. Install Lovely Injector following their instructions
2. Install Python dependencies: `pip install -r requirements.txt`
3. Launch Balatro with Lovely Injector enabled (more details in lovely-injector docs)
4. Run the Python training script: `python -m ai.train_balatro`

## Architecture

- **RLBridge Mod**: Lua mod using Lovely's patching system to hook into game state
- **Named Pipes**: Dual-pipe system (`/tmp/balatro_request`, `/tmp/balatro_response`) for communication.
- **Python Environment**: Custom Gym environment for RL training
- **Replay System**: JSON-based storage of winning game sequences

## Future Work

- Explore training parallelization (possibly via Docker/multiple instances)

---

## Development Notes (Personal)

Symlink for development (Arch Linux with Proton):
```bash
ln -s ~/dev/balatro-rl/RLBridge /mnt/gamerlinuxssd/SteamLibrary/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/RLBridge
```
