--- RLBridge utility module
--- Common helper functions for debugging, table operations, and state management
--- Provides tools for development and troubleshooting

local UTIL = {}
UTIL.completed_success_msg = "completed successfully"

-- Logging Functions
--- Log with AI prefix
--- @param msg string Message to log
UTIL.log_ai = function(msg)
    print("[AI] " .. msg)
end

--- Log with AI Dummy prefix (for auto-play testing)
--- @param msg string Message to log
UTIL.log_ai_dummy = function(msg)
    print("[AI DUMMY] " .. msg)
end

--- Log with communication prefix
--- @param msg string Message to log
UTIL.log_comm = function(msg)
    print("[COMM] " .. msg)
end

--- Log with input prefix
--- @param msg string Message to log
UTIL.log_input = function(msg)
    print("[INPUT] " .. msg)
end

--- Log with error prefix
--- @param msg string Message to log
UTIL.log_error = function(msg)
    print("[ERROR] " .. msg)
end

--- Log with testing prefix
--- @param msg string Message to log
UTIL.log_testing = function(msg)
    print("[TESTING] " .. msg)
end

--- Convert state ID to readable name
--- Maps numeric state IDs to their string representations for debugging
--- @param state_id number Numeric state identifier
--- @return string Human-readable state name or "UNKNOWN_STATE"
function UTIL.get_state_name(state_id)
    for key, value in pairs(G.STATES) do
        if value == state_id then
            return key
        end
    end
    return "UNKNOWN_STATE"
end

--- Simple table dump for debugging
--- Prints all key-value pairs in a table
--- @param table table Table to dump
--- @return nil
function UTIL.dump_table(table)
    for k, v in pairs(table) do
        print(k, v)
    end
end

--- Deep table dump with recursion protection
--- Recursively prints table contents with proper indentation
--- @param tbl table Table to dump
--- @param indent number|nil Current indentation level
--- @param visited table|nil Recursion tracking table
--- @return string Formatted table contents
function UTIL.dump_everything(tbl, indent, visited)
    indent = indent or 0
    visited = visited or {}

    local prefix = string.rep("  ", indent)
    local output = {}

    if visited[tbl] then
        table.insert(output, prefix .. "*RECURSION*")
        return table.concat(output, "\n")
    end

    visited[tbl] = true

    if type(tbl) ~= "table" then
        return tostring(tbl)
    end

    local keys = {}
    for k in pairs(tbl) do table.insert(keys, k) end
    table.sort(keys, function(a, b) return tostring(a) < tostring(b) end)

    for _, k in ipairs(keys) do
        local v = tbl[k]
        local key = tostring(k)
        local value_type = type(v)

        if value_type == "table" then
            table.insert(output, prefix .. key .. " = {")
            table.insert(output, UTIL.dump_everything(v, indent + 1, visited))
            table.insert(output, prefix .. "}")
        elseif value_type == "function" then
            table.insert(output, prefix .. key .. " = <function>")
        elseif value_type == "userdata" then
            table.insert(output, prefix .. key .. " = <userdata>")
        elseif value_type == "thread" then
            table.insert(output, prefix .. key .. " = <thread>")
        else
            local val_str = tostring(v)
            if value_type == "string" then
                val_str = '"' .. val_str .. '"'
            end
            table.insert(output, prefix .. key .. " = " .. val_str)
        end
    end

    return table.concat(output, "\n")
end

--- Helper function to get action names for logging
--- Converts action IDs to readable names for debug output
--- @param available_actions table Available actions table with IDs
--- @return table Array of action names
function UTIL.get_action_names(available_actions)
    local action = require("actions")
    local names = {}
    for action_id, _ in pairs(available_actions) do
        table.insert(names, action.get_action_name(action_id))
    end
    return names
end

function UTIL.contains(tbl, val)
    for x, _ in ipairs(tbl) do
        if tbl[x] == val then
            return true
        end
    end
    return false
end

--- Get current timestamp as formatted string
--- Returns current time in HH:MM:SS.mmm format for debugging
--- @return string Formatted timestamp
function UTIL.get_timestamp()
    local time = os.time()
    local ms = (os.clock() % 1) * 1000
    return os.date("%H:%M:%S", time) .. string.format(".%03d", ms)
end

return UTIL
