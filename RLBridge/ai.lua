--- RLBridge AI controller module
--- Main AI loop that handles state monitoring, action execution, and communication
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

    -- Don't continue if state = -1
    if current_state.state == -1 then
        return
    end

    -- Don't continue if there are no actions for the AI to do
    if next(current_state.available_actions) == nil then
        return
    end

    -- Create simple hash to detect state changes
    local state_hash = AI.hash_state(current_state)
    local actions_hash = AI.hash_actions(current_state.available_actions)

    -- Send state update if anything meaningful changed
    if state_hash ~= last_state_hash then
        utils.log_ai("State changed to: " .. current_state.state .. " (" .. utils.state_name(current_state.state) .. ")")
        action.reset_state()
        communication.send_state(current_state)
        last_state_hash = state_hash
    end

    -- Send actions update if available actions changed
    if actions_hash ~= last_actions_hash then
        utils.log_ai("Available actions changed")
        communication.send_actions(current_state.available_actions)
        last_actions_hash = actions_hash
    end

    -- Check for incoming actions from AI
    local ai_action = communication.receive_action()
    if ai_action then
        pending_action = ai_action
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

    -- TODO TODO Fallback: Auto-play for testing (remove this when AI is connected)
    AI.auto_play_fallback(current_state)
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

--- TESTING TESTING TESTING TESTING
--- Simple fallback AI for testing ONLY - DO NOT USE FOR REAL AI
--- This is purely for testing input mechanisms and game flow
--- Automatically selects blinds when no real AI is connected
--- @param game_state table Current game state data
--- @return nil
function AI.auto_play_fallback(game_state)
    -- Only auto-play if no real AI is connected and actions are available
    if not communication.is_connected() or pending_action then
        return
    end

    -- Auto-select blind for testing
    if game_state.state == G.STATES.MENU and game_state.available_actions[action.START_RUN] then
        local result = action.execute_action(action.START_RUN, {}) -- TODO consolidate this pattern
        if result.success then
            utils.log_ai_dummy("Auto start run executed")
        else
            utils.log_error("Auto Action failed: " .. (result.error or "Unknown Error"))
        end
    end
    if game_state.state == G.STATES.BLIND_SELECT and game_state.available_actions[action.SELECT_BLIND] then
        local result = action.execute_action(action.SELECT_BLIND, {})
        if result.success then
            utils.log_ai_dummy("Auto blind selection executed")
        else
            utils.log_error("Auto Action failed: " .. (result.error or "Unknown Error"))
        end
    end
    if game_state.state == G.STATES.SELECTING_HAND and game_state.available_actions[action.SELECT_HAND] then
        local result = action.execute_action(action.SELECT_HAND, { card_indices = { 1, 3, 5 } }) -- TODO for now of course
        if result.success then
            utils.log_testing(utils.dump_everything(output.get_game_state()))
            utils.log_ai_dummy("Auto selecting hand")
        else
            utils.log_error("Auto Action failed: " .. (result.error or "Unknown Error"))
        end
    end
end

return AI
