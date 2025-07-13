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

--- Initialize AI system
--- Sets up communication and prepares the AI for operation
--- @return nil
function AI.init()
    utils.log_ai("Initializing AI system...")
    communication.init()
end

--- Main AI update loop (called every frame)
--- Monitors game state changes, handles communication, and executes AI actions
--- @return nil
function AI.update()
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

    -- Create simple hash to detect state changes
    local state_hash = AI.hash_state(current_state)
    local actions_hash = AI.hash_actions(available_actions)

    -- Request action from AI if state or actions changed
    if state_hash ~= last_state_hash or actions_hash ~= last_actions_hash then
        if state_hash ~= last_state_hash then
            utils.log_ai("State changed to: " ..
                current_state.state .. " (" .. utils.state_name(current_state.state) .. ")")
            action.reset_state()
            last_state_hash = state_hash
        end

        if actions_hash ~= last_actions_hash then
            utils.log_ai("Available actions changed: " ..
                table.concat(utils.get_action_names(available_actions), ", "))
            last_actions_hash = actions_hash
        end

        -- Request action from AI via file I/O
        local ai_response = communication.request_action(current_state, available_actions)
        if ai_response and ai_response.action ~= "no_action" then
            pending_action = ai_response
        end
    end

    -- Execute pending action
    if pending_action then
        local result = action.execute_action(pending_action.action, pending_action.params)
        if result.success then
            utils.log_ai("Action executed successfully: " .. pending_action.action)
        else
            utils.log_ai("Action failed: " .. (result.error or "Unknown error"))
        end
        pending_action = nil
    end
end

--- Create simple hash of game state for change detection
--- Combines state, round, and chips into a unique identifier
--- @param game_state table Current game state data
--- @return string Hash representing the current state
function AI.hash_state(game_state)
    return game_state.state .. "_" .. (game_state.round or 0) .. "_" .. (game_state.chips or 0)
end

--- Create simple hash of available actions
--- Sorts action names and concatenates them for comparison
--- @param actions table Available actions table
--- @return string Hash representing available actions
function AI.hash_actions(actions)
    local action_names = {}
    for action_name, _ in pairs(actions) do
        table.insert(action_names, action_name)
    end
    table.sort(action_names)
    return table.concat(action_names, ",")
end

return AI
