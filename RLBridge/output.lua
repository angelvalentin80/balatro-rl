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

    local game_win = 0
    if G.STATE == G.STATES.ROUND_EVAL then
        game_win = 1
    end

    return {
        -- Basic state info
        state = G.STATE,
        game_over = game_over,
        game_win = game_win,

        -- Round info (hands/discards left)
        round = O.get_round_info(),

        -- Current blind chip requirement
        blind_chips = O.get_blind_chips(),

        -- Hand info (cards in hand)
        hand = O.get_hand_info(),

        -- Current total chips
        chips = G.GAME and G.GAME.chips or 0,

        -- Current hand scoring (chips × mult = score)
        current_hand = O.get_current_hand_scoring(),

        -- Current seed
        seed = G.GAME and G.GAME.pseudorandom.seed or 0,
    }
end

--- Get blind chip requirement 
--- @return number Chips needed to beat current blind
function O.get_blind_chips()
    if not G.GAME or not G.GAME.blind then
        return 300  -- TODO probably fix this if we are doing more than one blind Default ante 1 small blind requirement
    end
    return G.GAME.blind.chips or 300
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


--- Get round information
--- Gets hands and discards left in the current round
--- @return table Round data with hands and discards remaining
function O.get_round_info()
    return {
        hands_left = G.GAME and G.GAME.current_round and G.GAME.current_round.hands_left or 0,
        discards_left = G.GAME and G.GAME.current_round and G.GAME.current_round.discards_left or 0,
    }
end


--- Get current hand scoring information
--- Extracts chips, mult, and potential score for current/highlighted hand
--- @return table Hand scoring data with defaults
function O.get_current_hand_scoring()
    -- Try to get current hand preview info
    local chips = 0
    local mult = 0
    local score = 0
    local handname = "None"
    
    if G.GAME and G.GAME.current_round and G.GAME.current_round.current_hand then
        chips = G.GAME.current_round.current_hand.chips or 0
        mult = G.GAME.current_round.current_hand.mult or 0
        score = G.GAME.current_round.current_hand.chip_total or (chips * mult)
        handname = G.GAME.current_round.current_hand.handname or "None"
    end
    
    return {
        chips = chips,
        mult = mult,
        score = score,
        handname = handname
    }
end

return O
