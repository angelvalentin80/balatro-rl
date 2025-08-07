# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a reinforcement learning project for the card game Balatro. The goal is to create a mod that can:
1. Extract game state data from Balatro
2. Allow an RL AI to observe the data and perform actions
3. Enable the AI to learn over time through gameplay
4. Facilitate speed as much as possible which means skipping animations, and timers whenever possible
5. We don't want to modify the game in any way to give an unfair advantage, we just want to play the game how it was designed

## Architecture

### RLBridge Mod Structure
The project uses the Lovely mod framework to inject code into Balatro. The main mod is located in `RLBridge/`

### Lovely Patching System
The mod uses `RLBridge/lovely/` to define patches:
- Any patch can be created in the lovely dir by creating a .toml file


### Balatro Source Code
The `balatro-source-code/` directory contains the decompiled Balatro source code for reference and understanding game internals.
Editing this file won't do nothing so don't edit it, it's just reference

## Development Setup

### Linux (Arch) with Proton
Create a symlink to the Steam mods directory:
```bash
ln -s ~/dev/balatro-rl/RLBridge /mnt/gamerlinuxssd/SteamLibrary/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/RLBridge
```

### Mod Dependencies
- Uses Lovely for code injection

## Key Implementation Details

### Game State Management
Balatro uses numbered states defined in `globals.lua`:
- `G.STATES.BLIND_SELECT = 7` - When player can choose blinds
- `G.STATES.SELECTING_HAND = 1` - When player selects cards to play
- `G.STATES.SHOP = 5` - In the shop between rounds

### Critical Patterns
- All mod functions are called from `ai.update()` which runs every frame
- Use flags to prevent repeated actions in frame-based updates
- Game state transitions happen through calling existing game functions rather than direct state manipulation
- UI elements may not exist immediately when states change

### Key Balatro Globals
- `G.STATE` - Current game state number
- `G.GAME` - Main game data structure
- `G.FUNCS` - Game function callbacks

## Communication Architecture

### Dual Pipe Communication
The mod uses separate named pipes for request/response communication with the AI:
- **Request pipe path**: `/tmp/balatro_request` (Balatro writes, AI reads)
- **Response pipe path**: `/tmp/balatro_response` (AI writes, Balatro reads)
- **Protocol**: Persistent pipe handles with blocking reads
- **Flow**: 
  1. Balatro opens persistent handles to both pipes
  2. Balatro writes JSON request to request pipe
  3. AI reads request from request pipe
  4. AI writes JSON response to response pipe
  5. Balatro performs blocking read from response pipe

### Benefits of Dual Pipes
- Clear separation of request/response channels
- Persistent handles avoid repeated open/close overhead
- Blocking reads ensure proper synchronization
- Each pipe has single direction, eliminating read/write conflicts

## Current Status
The mod can successfully:
- Start a run automatically
- Detect blind selection state
- Automatically select the next blind
- Communicate with AI via dual pipe system

## Communication with Claude
- Please keep chats as efficient as possible and brief. No fluff talk, just get to the point
- Try to break things down in first principles effectively
