--- RLBridge communication module
--- Handles communication between the game and external AI system
--- Currently simulated, will be replaced with actual socket implementation
---
--- TODO make sure we send the whole game state in the moment that the game is ready for input to AI
--- TODO we shouldn't send state and game_state separately. It should just be one comm
--- TODO we should only send state too when there's an action available from the AI. like the AI just knowing that the
--- sate is "SELECT_HAND" doesn't do anything if there are no available actions

local COMM = {}
local utils = require("utils")
local action = require("actions")

-- Socket communication (placeholder for now)
-- You'll need to implement actual socket connection later
local socket_connected = false
local message_queue = {}

--- Initialize socket connection
--- Sets up communication channel with external AI system
--- @return nil
function COMM.init()
    utils.log_comm("Initializing communication...")
    -- TODO: Set up actual socket connection
    -- For now, just simulate connection
    socket_connected = true
    utils.log_comm("Ready (simulated)")
end

--- Send game state to AI
--- Transmits current game state data to the external AI system
--- @param game_state table Current game state data
--- @return boolean True if sent successfully, false otherwise
function COMM.send_state(game_state)
    if not socket_connected then
        return false
    end

    local message = {
        type = "state_update",
        timestamp = os.time(), -- or use G.TIMERS.REAL for game time
        data = game_state
    }

    -- TODO: Replace with actual socket send
    utils.log_comm("Sending state: " .. tostring(game_state.state))
    -- For debugging, you could write to a file here

    return true
end

--- Send available actions to AI
--- Transmits list of currently available actions to the AI system
--- @param available_actions table Available actions with options
--- @return boolean True if sent successfully, false otherwise
function COMM.send_actions(available_actions)
    if not socket_connected then
        return false
    end

    local message = {
        type = "actions_available",
        timestamp = os.time(),
        actions = available_actions
    }

    -- TODO: Replace with actual socket send
    utils.log_comm("Available actions: " .. table.concat(COMM.get_action_names(available_actions), ", "))

    return true
end

--- Receive action from AI (placeholder)
--- Gets the next action command from the external AI system
--- @return table|nil Action data if available, nil otherwise
function COMM.receive_action()
    if not socket_connected then
        return nil
    end

    -- TODO: Replace with actual socket receive
    -- For now, return nil (no action from AI)
    return nil

    -- Example of what this should return:
    -- return {
    --     type = "action",
    --     action = "select_blind",
    --     params = {blind_type = "small"},
    --     request_id = "abc123"
    -- }
end

--- Helper function to get action names from available actions
--- Extracts just the action names for logging and debugging
--- @param available_actions table Available actions table
--- @return table Array of action names
function COMM.get_action_names(available_actions)
    local names = {}
    for action_id, _ in pairs(available_actions) do
        table.insert(names, action.get_action_name(action_id))
    end
    return names
end

--- Check if socket is connected
--- Returns the current connection status
--- @return boolean True if connected, false otherwise
function COMM.is_connected()
    return socket_connected
end

--- Close connection
--- Terminates the communication channel with the AI system
--- @return nil
function COMM.close()
    socket_connected = false
    utils.log_comm("Connection closed")
end

return COMM
