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

## TODO
### Connect Balatro to real AI
- Socket communication
- RL python working
### AI Necessities
- Make it so that the AI can choose between skipping blind or selecting blind instead of auto selecting
- Get access to state like money, discards, hands played etc
