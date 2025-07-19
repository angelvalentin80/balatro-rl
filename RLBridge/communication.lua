--- RLBridge communication module
--- Handles dual pipe communication with persistent handles between the game and external AI system

local COMM = {}
local utils = require("utils")
local json = require("dkjson")

-- Dual pipe communication settings with persistent handles
local comm_enabled = false
local request_pipe = "/tmp/balatro_request"
local response_pipe = "/tmp/balatro_response"
local request_handle = nil
local response_handle = nil

--- Initialize dual pipe communication with persistent handles
--- Sets up persistent pipe handles with external AI system
--- @return nil
function COMM.init()
    utils.log_comm("Initializing dual pipe communication with persistent handles...")
    utils.log_comm("Note: Pipes will be opened when first needed (lazy initialization)")
    comm_enabled = true -- Enable communication, pipes will open on first use
end

--- Lazy initialization of pipe handles when first needed
--- @return boolean True if pipes are ready, false otherwise
function COMM.ensure_pipes_open()
    if request_handle and response_handle then
        return true -- Already open
    end

    -- Try to open pipes (this will block until AI creates them)
    utils.log_comm("Opening persistent pipe handles...")

    -- Open response pipe for reading (keep open)
    response_handle = io.open(response_pipe, "r")
    if not response_handle then
        utils.log_comm("ERROR: Cannot open response pipe for reading: " .. response_pipe)
        return false
    end

    -- Open request pipe for writing (keep open)
    request_handle = io.open(request_pipe, "w")
    if not request_handle then
        utils.log_comm("ERROR: Cannot open request pipe for writing: " .. request_pipe)
        if response_handle then
            response_handle:close()
            response_handle = nil
        end
        return false
    end

    utils.log_comm("Persistent pipe handles opened successfully")
    utils.log_comm("Request pipe (write): " .. request_pipe)
    utils.log_comm("Response pipe (read): " .. response_pipe)
    return true
end

--- Send game turn request to AI and get action via persistent pipe handles
--- @param game_state table Current game state data
--- @param available_actions table Available actions list
--- @return table|nil Action response from AI, nil if error
function COMM.request_action(game_state, available_actions, retry_count)
    if not comm_enabled then
        utils.log_comm("ERROR: Communication not enabled")
        return nil
    end

    -- Lazy initialization - open pipes when first needed
    if not COMM.ensure_pipes_open() then
        utils.log_comm("ERROR: Failed to open pipe handles")
        return nil
    end

    local request = {
        game_state = game_state,
        available_actions = available_actions or {},
        retry_count = retry_count,
    }

    utils.log_comm(utils.get_timestamp() .. "Sending action request for state: " ..
        tostring(game_state.state) .. " (" .. utils.get_state_name(game_state.state) .. ")")

    -- Encode request as JSON
    local json_data = json.encode(request)
    if not json_data then
        utils.log_comm("ERROR: Failed to encode request JSON")
        return nil
    end

    -- Write request to persistent handle
    request_handle:write(json_data .. "\n")
    request_handle:flush() -- Ensure data is sent immediately
    utils.log_comm(utils.get_timestamp() .. "Request sent...")

    -- Read response from persistent handle
    utils.log_comm(utils.get_timestamp() .. "about to read the respones")
    local response_json = response_handle:read("*line")

    if not response_json or response_json == "" then
        utils.log_comm("ERROR: No response received from AI")
        return nil
    end

    local response_data = json.decode(response_json)
    if not response_data then
        utils.log_comm("ERROR: Failed to decode response JSON")
        return nil
    end

    utils.log_comm("AI action: " .. tostring(response_data.action))
    return response_data
end

--- Check if pipe communication is enabled
--- Returns the current communication status
--- @return boolean True if enabled, false otherwise
function COMM.is_connected()
    return comm_enabled
end

--- Close communication
--- Terminates the persistent pipe handles with the AI system
--- @return nil
function COMM.close()
    comm_enabled = false

    if request_handle then
        request_handle:close()
        request_handle = nil
    end

    if response_handle then
        response_handle:close()
        response_handle = nil
    end

    utils.log_comm("Persistent pipe communication closed")
end

return COMM
