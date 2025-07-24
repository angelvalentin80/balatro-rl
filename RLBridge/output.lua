--- RLBridge output module
--- Extracts and formats game state data for AI consumption
--- Provides comprehensive game information including cards, chips, and available actions

local O = {}

--- Get comprehensive game state for AI
--- Collects all relevant game information into a structured format
--- @return table Complete game state data for AI processing
function O.get_game_state()
    -- Calculate game_over
    local game_over = 0
    if G.STATE == G.STATES.GAME_OVER then
        game_over = 1
    end

    return {
        -- Basic state info
        state = G.STATE,
        game_over = game_over,

        -- Round info
        round = O.get_round_info(),

        -- Ante info
        ante = O.get_ante_info(),

        -- Current blind info (if in a round)
        blind = O.get_current_blind_info(),

        -- Hand info (if applicable)
        hand = O.get_hand_info(),

        -- Chips/score info
        chips = G.GAME and G.GAME.chips or 0,
    }
end

--- Get current blind information
--- Extracts details about the current blind being played
--- @return table Blind data with defaults if not available
function O.get_current_blind_info()
    if not G.GAME or not G.GAME.blind then
        return {
            type = "None",
            chips = 0,
            dollars = 0,
            defeated = false,
            blind_ante = 0,
        }
    end

    return {
        type = G.GAME.blind:get_type() or "None",
        chips = G.GAME.blind.chips or 0,
        dollars = G.GAME.blind.dollars or 0,
        defeated = G.GAME.blind.defeated or false,
        blind_ante = G.GAME.round_resets.blind_ante or 0,
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
            base = {
                nominal = card.base.nominal or 0,
                value = card.base.value or ""
            },
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

--- Get round information
--- Gets hands and discards left in the current round
--- @return table Round data with hands and discards remaining
function O.get_round_info()
    return {
        hands_left = G.GAME and G.GAME.current_round and G.GAME.current_round.hands_left or 0,
        discards_left = G.GAME and G.GAME.current_round and G.GAME.current_round.discards_left or 0,
    }
end

--- Get ante information
--- Gets all of the important information necessary for antes
--- @return table Ante data with defaults if not available
function O.get_ante_info()
    if not G.GAME or not G.GAME.round_resets then
        return {
            win_ante = 8,
            current_ante = 0,
        }
    end

    return {
        win_ante = G.GAME.win_ante or 8,
        current_ante = G.GAME.round_resets.ante or 0,
    }
end

return O
