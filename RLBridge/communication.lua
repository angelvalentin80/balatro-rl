--- RLBridge communication module
--- Handles file-based communication between the game and external AI system

local COMM = {}
local utils = require("utils")
local action = require("actions")
local json = require("dkjson")

-- File-based communication settings
local comm_enabled = false
local request_file = "/tmp/balatro_request.json"
local response_file = "/tmp/balatro_response.json"
local request_counter = 0
local last_response_time = 0

--- Check if response file has new content
--- @param expected_id number Expected request ID
--- @return table|nil Response data if new response available, nil otherwise
local function check_for_response(expected_id)
    local response_file_handle = io.open(response_file, "r")
    if not response_file_handle then
        return nil
    end

    local response_json = response_file_handle:read("*all")
    response_file_handle:close()

    if not response_json or response_json == "" then
        return nil
    end

    local response_data = json.decode(response_json)
    if not response_data then
        return nil
    end

    -- Check if this is a new response for our request
    if response_data.id == expected_id and response_data.timestamp then
        if response_data.timestamp > last_response_time then
            last_response_time = response_data.timestamp
            return response_data
        end
    end

    return nil
end

--- Initialize file-based communication
--- Sets up file-based communication channel with external AI system
--- @return nil
function COMM.init()
    utils.log_comm("Initializing file-based communication...")
    comm_enabled = true
    last_response_time = 0 -- Reset response tracking

    utils.log_comm("Ready for file-based requests")
    utils.log_comm("Request file: " .. request_file)
    utils.log_comm("Response file: " .. response_file)
end

--- Send game turn request to AI and get action via files
--- @param game_state table Current game state data
--- @param available_actions table Available actions list
--- @return table|nil Action response from AI, nil if error
function COMM.request_action(game_state, available_actions)
    if not comm_enabled then
        return nil
    end

    request_counter = request_counter + 1

    local request = {
        id = request_counter,
        timestamp = os.time(),
        game_state = game_state,
        available_actions = available_actions or {}
    }

    utils.log_comm("Requesting action for state: " .. tostring(game_state.state))

    -- Write request to file
    local json_data = json.encode(request)
    if not json_data then
        utils.log_comm("ERROR: Failed to encode request JSON")
        return nil
    end

    local request_file_handle = io.open(request_file, "w")
    if not request_file_handle then
        utils.log_comm("ERROR: Cannot write to request file: " .. request_file)
        return nil
    end

    request_file_handle:write(json_data)
    request_file_handle:close()

    -- Wait for response file (with timeout)
    local max_wait_time = 2    -- seconds
    local wait_interval = 0.05 -- seconds
    local total_waited = 0

    while total_waited < max_wait_time do
        local response_data = check_for_response(request_counter)
        if response_data then
            utils.log_comm("AI action: " .. tostring(response_data.action))
            return response_data
        end

        -- Sleep for a short time using busy wait
        local start_time = os.clock()
        while (os.clock() - start_time) < wait_interval do
            -- Busy wait for short duration
        end
        total_waited = total_waited + wait_interval
    end

    utils.log_comm("ERROR: Timeout waiting for AI response")
    return nil
end

--- Check if file communication is enabled
--- Returns the current communication status
--- @return boolean True if enabled, false otherwise
function COMM.is_connected()
    return comm_enabled
end

--- Close communication
--- Terminates the communication channel with the AI system
--- @return nil
function COMM.close()
    comm_enabled = false
    last_response_time = 0
    utils.log_comm("File communication disabled")
end

return COMM
