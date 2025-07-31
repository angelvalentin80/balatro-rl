--- RLBridge AI controller module
--- Main AI loop that handles state monitoring, action execution, and file-based communication
--- Runs every frame and coordinates between game state observation and AI decisions

local AI = {}

local output = require("output")
local action = require("actions")
local communication = require("communication")
local utils = require("utils")

-- State management
local last_combined_hash = nil
local pending_action = nil
local need_retry_request = false
local rl_training_active = false
local last_key_pressed = nil

--- Initialize AI system
--- Sets up communication and prepares the AI for operation
--- @return nil
function AI.init()
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
                utils.log_ai("\n\nRL Training STARTED (R pressed)")
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

    -- Create combined hash to detect meaningful changes
    local combined_hash = AI.hash_combined_state(current_state, available_actions)

    if combined_hash ~= last_combined_hash or need_retry_request then
        -- Game state or available actions have changed
        utils.log_ai("State/Actions changed: State: " ..
            current_state.state .. " (" .. utils.get_state_name(current_state.state) .. ") | " ..
            "Actions: " .. table.concat(utils.get_action_names(available_actions), ", "))

        action.reset_state()

        -- Request action from AI
        need_retry_request = false
        local ai_response = communication.request_action(current_state, available_actions)

        if ai_response then
            -- Handling handshake
            if ai_response.action == "ready" then
                utils.log_ai("Handshake complete - AI ready")
                -- Force a state check on next frame to send real request
                last_combined_hash = nil
            else
                pending_action = ai_response
                last_combined_hash = combined_hash
            end
        end
    end

    -- Execute pending action
    if pending_action then
        -- Validate action is still available in current state
        local current_actions = action.get_available_actions()
        local action_still_valid = false
        for _, valid_action in ipairs(current_actions) do
            if valid_action == pending_action.action then
                action_still_valid = true
                break
            end
        end
        
        if action_still_valid then
            local result = action.execute_action(pending_action.action, pending_action.params)
            if result.success then
                utils.log_ai("Action executed successfully: " .. pending_action.action)
            else
                utils.log_ai("Action failed: " .. (result.error or "Unknown error") .. " RETRYING...")
                need_retry_request = true
            end
        else
            utils.log_ai("Action no longer valid (state changed), discarding: " .. pending_action.action)
            -- Force a retry to get a new action for the current state
            need_retry_request = true
        end
        pending_action = nil
        utils.log_ai("\n\n\n")
    end
end

--- Create combined hash of game state and actions for change detection
--- Only sends AI requests when both state and actions are ready/changed
--- @param game_state table Current game state data
--- @param available_actions table Available actions list
--- @return string Combined hash representing state + actions
function AI.hash_combined_state(game_state, available_actions)
    -- State components
    local state_parts = {
        game_state.state or 0,
        game_state.chips or 0,
        game_state.blind_chips or 0,
        (game_state.round and game_state.round.hands_left) or 0,
        (game_state.round and game_state.round.discards_left) or 0,
        (game_state.hand and game_state.hand.size) or 0,
        (game_state.hand and game_state.hand.highlighted_count) or 0,
        game_state.game_over or 0
    }

    -- Action components
    local action_ids = {}
    for _, id in ipairs(available_actions) do
        table.insert(action_ids, tostring(id))
    end
    table.sort(action_ids)

    -- Combine everything
    local combined = table.concat(state_parts, "_") .. "|" .. table.concat(action_ids, ",")
    return combined
end

return AI
