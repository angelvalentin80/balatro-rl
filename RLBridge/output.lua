--- RLBridge output module
--- Extracts and formats game state data for AI consumption
--- Provides comprehensive game information including cards, chips, and available actions

local O = {}

local actions = require("actions")

--- Get comprehensive game state for AI
--- Collects all relevant game information into a structured format
--- @return table Complete game state data for AI processing
function O.get_game_state()
    return {
        -- Basic state info
        state = G.STATE,

        -- Available actions for AI
        available_actions = actions.get_available_actions(),

        -- Game progression
        -- round = G.GAME and G.GAME.round or 0,
        -- ante = G.GAME and G.GAME.round_resets and G.GAME.round_resets.ante or 0,

        -- -- Resources
        -- dollars = G.GAME and G.GAME.dollars or 0,

        -- Current blind info (if in a round)
        blind = O.get_current_blind_info(),

        -- Hand info (if applicable)
        hand = O.get_hand_info(),

        -- -- Jokers info
        -- jokers = O.get_jokers_info(),

        -- -- Chips/score info
        -- chips = G.GAME and G.GAME.chips or 0,
        -- chip_target = G.GAME and G.GAME.blind and G.GAME.blind.chips or 0,

        -- -- Action feedback for AI
        -- last_action_success = true, -- Did last action work?
        -- last_action_error = nil,    -- What went wrong?
    }
end

--- Get current blind information
--- Extracts details about the current blind being played
--- @return table|nil Blind data if available, nil otherwise
function O.get_current_blind_info()
    if not G.GAME or not G.GAME.blind then
        return nil
    end

    return {
        name = G.GAME.blind.name or "Unknown",
        type = G.GAME.blind:get_type(),
        chips = G.GAME.blind.chips or 0,
        dollars = G.GAME.blind.dollars or 0,
        defeated = G.GAME.blind.defeated or false
    }
end

--- Get hand information
--- Extracts player's current hand cards and selection state
--- @return table Hand data with cards and metadata
function O.get_hand_info()
    if not G.hand or not G.hand.cards then
        return { cards = {}, size = 0, highlighted_count = 0 }
    end

    local hand_cards = {}
    for _, card in ipairs(G.hand.cards) do
        table.insert(hand_cards, {
            ability = {
                bonus = card.ability.bonus or 0,
                h_dollars = card.ability.h_dollars or 0,
                h_x_mult = card.ability.h_x_mult or 0,
                mult = card.ability.mult or 0,
                p_dollars = card.ability.p_dollars or 0,
                perma_bonus = card.ability.perma_bonus or 0,
                t_chips = card.ability.t_chips or 0,
                t_mult = card.ability.t_mult or 0,
                type = card.ability.type or "",
                x_mult = card.ability.x_mult or 1
            },
            base = {
                nominal = card.base.nominal or 0,
                value = card.base.value or ""
            },
            cost = card.cost or 0,
            debuff = card.debuff or false,
            highlighted = card.highlighted or false,
            suit = card.base.suit or ""
        })
    end

    return {
        cards = hand_cards,
        size = #hand_cards,
        highlighted_count = G.hand.highlighted and #G.hand.highlighted or 0
    }
end

--- Get joker information
--- Extracts all joker cards currently owned by the player
--- @return table Joker data with names and identifiers
function O.get_jokers_info()
    if not G.jokers or not G.jokers.cards then
        return { cards = {}, count = 0 }
    end

    local joker_cards = {}
    for i, joker in ipairs(G.jokers.cards) do
        table.insert(joker_cards, {
            name = joker.config and joker.config.center and joker.config.center.name or "Unknown",
            key = joker.config and joker.config.center and joker.config.center.key or "unknown",
            id = joker.sort_id or i
        })
    end

    return {
        cards = joker_cards,
        count = #joker_cards
    }
end

return O
