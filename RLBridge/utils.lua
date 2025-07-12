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
function UTIL.state_name(state_id)
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

return UTIL
