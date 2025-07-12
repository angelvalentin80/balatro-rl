--- RLBridge initialization module
--- Handles initial game setup and configuration for the RL system
--- Sets up animation skipping and starts a new Balatro run with AI integration

local INIT = {}

DISABLE_ANIMATIONS = true
G.SETTINGS.skip_splash = 'Yes'
G.SETTINGS.GAMESPEED = 100
G.SETTINGS.reduced_motion = true

--- Should be called after G:start_up() to safely initialize and start a run
--- Initializes the AI system and starts a new Balatro run with default settings
--- @return nil
function INIT.start_run()
    print("Starting balatro run")

    -- Initialize AI system
    local ai = require("ai")
    ai.init()
end

return INIT
