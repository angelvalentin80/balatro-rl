--- RLBridge AI controller module
--- Main AI loop that handles state monitoring, action execution, and file-based communication
--- Runs every frame and coordinates between game state observation and AI decisions

local AI = {}

local output = require("output")
local action = require("actions")
local communication = require("communication")
local utils = require("utils")

-- State management
local last_state_hash = nil
local last_actions_hash = nil
local pending_action = nil
local retry_count = 0
local need_retry_request = false
local rl_training_active = false
local last_key_pressed = nil

--- Initialize AI system
--- Sets up communication and prepares the AI for operation
--- @return nil
function AI.init()
    utils.log_ai("Initializing AI system...")
    communication.init()

    -- Hook into Love2D keyboard events
    if love and love.keypressed then
        local original_keypressed = love.keypressed
        love.keypressed = function(key)
            -- Store the key press for our AI
            last_key_pressed = key

            -- Call original function
            if original_keypressed then
                original_keypressed(key)
            end
        end
    else
    end
end

--- Main AI update loop (called every frame)
--- Monitors game state changes, handles communication, and executes AI actions
--- @return nil
function AI.update()
    -- Check for key press to start/stop RL training
    if last_key_pressed then
        if last_key_pressed == "r" then
            if not rl_training_active then
                rl_training_active = true
                utils.log_ai("🚀 RL Training STARTED (R pressed)")
            end
        elseif last_key_pressed == "t" then
            if rl_training_active then
                rl_training_active = false
                utils.log_ai("⏹️ RL Training STOPPED (T pressed)")
            end
        end

        -- Clear the key press
        last_key_pressed = nil
    end

    -- Don't process AI requests unless RL training is active
    if not rl_training_active then
        return
    end

    -- Get current game state
    local current_state = output.get_game_state()
    local available_actions = action.get_available_actions()

    -- Don't continue if state = -1
    if current_state.state == -1 then
        return
    end

    -- Don't continue if there are no actions for the AI to do
    if next(available_actions) == nil then
        return
    end

    -- Create hash to detect state changes
    local state_hash = AI.hash_state(current_state)
    local actions_hash = AI.hash_actions(available_actions)

    if state_hash ~= last_state_hash or actions_hash ~= last_actions_hash or need_retry_request then
        -- State has changed
        if state_hash ~= last_state_hash then
            utils.log_ai("State changed to: " ..
                current_state.state .. " (" .. utils.get_state_name(current_state.state) .. ")")
            action.reset_state()
            last_state_hash = state_hash
        end

        -- Available actions have changed
        if actions_hash ~= last_actions_hash then
            utils.log_ai("Available actions changed: " ..
                table.concat(utils.get_action_names(available_actions), ", "))
            last_actions_hash = actions_hash
        end

        -- Request action from AI
        need_retry_request = false
        local ai_response = communication.request_action(current_state, available_actions, retry_count)

        if ai_response then
            -- Handling handshake
            if ai_response.action == "ready" then
                utils.log_ai("Handshake complete - AI ready")
                -- Don't return - continue normal game loop
                -- Force a state check on next frame to send real request
                last_state_hash = nil
            else
                pending_action = ai_response
            end
        end
    end

    -- Execute pending action
    if pending_action then
        local result = action.execute_action(pending_action.action, pending_action.params)
        if result.success then
            utils.log_ai("Action executed successfully: " .. pending_action.action)
            retry_count = 0
        else
            -- Update retry_count to indicate state change
            utils.log_ai("Action failed: " .. (result.error or "Unknown error") .. " RETRYING...")
            retry_count = retry_count + 1
            need_retry_request = true
        end
        pending_action = nil
    end
end

--- Create simple hash of game state for change detection
--- Combines state, round, and chips into a unique identifier
--- @param game_state table Current game state data
--- @return string Hash representing the current state
function AI.hash_state(game_state)
    return game_state.state .. "_" .. (game_state.chips or 0) -- TODO update hash to be more unique
end

--- Create simple hash of available actions
--- Sorts action names and concatenates them for comparison
--- @param actions table Available actions table
--- @return string Hash representing available actions
function AI.hash_actions(actions)
    local action_ids = {}
    for _, id in ipairs(actions) do
        table.insert(action_ids, id)
    end
    table.sort(action_ids)
    return table.concat(action_ids, ",")
end

return AI
