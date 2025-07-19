# balatro-rl

## Reinforcement Learning in Balatro

The goal is the follow:
- Make a mod for Balatro to read data and do certain actions
- Have a reinforcement learning ai see that data and perform actions and learn over time


## How to set up
- Use this to figure out how to setup smodded -> https://github.com/Steamodded/smods

I am currenly on Arch Linux, so I had to follow the setup through Proton
Currently writing code in a more reliable directory and having it symlink to the correct directory mods folder
Made a symlink -> ln -s ~/dev/balatro-rl/RLBridge /mnt/gamerlinuxssd/SteamLibrary/steamapps/compatdata/2379780/pfx/drive_c/users/steamuser/AppData/Roaming/Balatro/Mods/RLBridge

## TODO/CHANGELOG
### File-based Communication
- [x] JSON file communication system
- [x] Lua file writer in mod
- [x] Python file watcher with watchdog
- [x] Game state transmission (hand cards, chips, available actions)
- [x] Action reception and execution

### RL Training
- [ ] Python RL environment setup
- [ ] AI model architecture
- [ ] Training loop integration

### Game Features  
- [ ] Always have restart_run as an action option assuming the game is ongoing
- [ ] Blind selection choices (skip vs select)
- [ ] Extended game state (money, discards, hands played)
- [ ] Shop interactions
- [ ] Joker management

### RL Enhancements
- [ ] Add a "Replay System" to analyze successful actions. For example, save seed, have an action log for reproduction etc 
Can probably do this by adding it before the game is reset like a check on what criteria I want to save for, and save
