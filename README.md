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
- [x] Python RL environment setup
- [x] AI model architecture
- [x] Training loop integration

### Game Features  
- [x] Always have restart_run as an action option assuming the game is ongoing
- [x] Make it so that if we lose, we can restart, or if we win a round and see the "cash out" 
page, then we also restart. but getting to the "cash out" state should give a ton of reward to incentivize
the AI
- [x] Should we add things that help the AI understand they have only 4 hands and 4 discards to work with? or whatever
number it is? I think we should add the hands and discards in the game state as well that would be useful
- [ ] Should we not give reward for just plain increasing chips? if you think about it, you can play anything and increase
chips. Perhpas we just want to get wins of rounds just scoring chips is not enough?. Wonder if the losing penatly is not enough
- [ ] Blind selection choices (skip vs select)
- [ ] Extended game state (money, discards, hands played)
- [ ] I wonder if there's a problem with the fact that they get points out of every hand played. I feel like
it should learn to play more complex hands instead of just getting points even if just one hand scores
we should maybe have the rewards reflect that
- [ ] Add some mechanism of finding out how many times the AI has won the game
- [ ] Is there a way to reward the AI for getting "fire" type scores which are really good
- [ ] Shop interactions
- [ ] Joker management

### RL Enhancements
- [ ] **Retry Count Penalty**: Penalize high retry_count in rewards to discourage invalid actions. Currently retry_count tracks failed action attempts, but we could use this signal to teach the AI which actions are actually valid in each state. Formula: `reward -= retry_count * penalty_factor`. This would incentivize the AI to learn valid action spaces rather than trial-and-error.
- [ ] Add a "Replay System" to analyze successful actions. For example, save seed, have an action log for reproduction etc 
Can probably do this by adding it before the game is reset like a check on what criteria I want to save for, and save
