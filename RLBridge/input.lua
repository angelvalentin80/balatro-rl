--- RLBridge input module
--- Handles direct game input actions like selecting blinds and making plays
--- Provides interface between AI actions and Balatro's internal functions

local I = {}
local utils = require("utils")

--- Start the basic run
--- Automatically starts the run in the main menu
--- @return table Result with success status and optional error message
function I.start_run()
    local _seed = G.run_setup_seed and G.setup_seed or G.forced_seed or nil
    local _challenge = G.challenge_tab or nil
    local _stake = G.forced_stake or G.PROFILES[G.SETTINGS.profile].MEMORY.stake or 1

    G.FUNCS.start_run(nil, {
        stake = _stake,
        seed = _seed,
        challenge = _challenge
    })
    utils.log_input("start_run " .. utils.completed_success_msg)
    return { success = true }
end

--- Select the current blind on deck
--- Automatically selects the next available blind in the blind selection screen
--- @return table Result with success status and optional error message
function I.select_blind()
    -- Get the blind that's on deck and just select it
    local blind_on_deck = G.GAME.blind_on_deck

    -- Create the button structure that select_blind expects
    local fake_button = {
        config = {
            ref_table = G.P_BLINDS[G.GAME.round_resets.blind_choices[blind_on_deck]],
            id = blind_on_deck
        }
    }

    G.FUNCS.select_blind(fake_button)
    utils.log_input("select_blind " .. utils.completed_success_msg)
    return { success = true }
end

--- Select a hand
--- Selects the cards based on a table of indexes
--- @param card_indices table Array of card indices to select
--- @return table Result with success status and optional error message
function I.select_hand(card_indices)
    if not card_indices or type(card_indices) ~= "table" then
        return { success = false, error = "Invalid card indices parameter" }
    end

    if #card_indices < 1 then
        return { success = false, error = "Must play minimum one card" }
    end
    if #card_indices > 5 then
        return { success = false, error = "Must play maximum 5 cards" }
    end

    -- Validate hand exists and has cards
    if not G.hand or not G.hand.cards or #G.hand.cards == 0 then
        return { success = false, error = "No hand or cards available" }
    end

    -- Validate all card indices are within bounds
    for i = 1, #card_indices do
        local card_index = card_indices[i]
        if not card_index or card_index < 1 or card_index > #G.hand.cards then
            return { success = false, error = "Card index out of bounds: " .. tostring(card_index) }
        end
        if not G.hand.cards[card_index] then
            return { success = false, error = "Card at index " .. card_index .. " does not exist" }
        end
    end

    -- Click the cards
    for i = 1, #card_indices do
        G.hand.cards[card_indices[i]]:click()
    end
    utils.log_input("select_hand " .. utils.completed_success_msg)
    return { success = true }
end

--- Click "Play Hand" button to play a hand that was selected
--- @return table Result with success status and optional error message
function I.play_hand()
    utils.log_input("play_hand " .. utils.completed_success_msg)
    G.FUNCS.play_cards_from_highlighted()
    return { success = true }
end

--- Click "Discard" button to discard a hand that was selected
--- @return table Result with success status and optional error message
function I.discard_hand()
    G.FUNCS.discard_cards_from_highlighted()
    utils.log_input("select_hand " .. utils.completed_success_msg)
    return { success = true }
end


return I
