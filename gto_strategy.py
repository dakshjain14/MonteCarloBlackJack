def get_gto_move(player_hand, dealer_upcard):
    dealer = dealer_upcard if dealer_upcard != 11 else 11
    
    # Split pairs based on dealer upcard
    if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
        pair = player_hand[0]
        if pair in [8, 11]: 
            return "split"
        if pair == 9 and dealer in [2, 3, 4, 5, 6, 8, 9]: 
            return "split"
        if pair == 7 and dealer in [2, 3, 4, 5, 6, 7]: 
            return "split"
        if pair == 6 and dealer in [2, 3, 4, 5, 6]: 
            return "split"
        if pair == 4 and dealer in [5, 6]: 
            return "split"
        if pair in [2, 3] and dealer in [2, 3, 4, 5, 6, 7]: 
            return "split"

    # Check if hand is soft (has an active 11) and get total
    raw_sum = sum(player_hand)
    aces = player_hand.count(11)
    
    while raw_sum > 21 and aces > 0:
        raw_sum -= 10
        aces -= 1
        
    is_soft = (aces > 0 and raw_sum <= 21)
    total = raw_sum

    # Double down only on first 2 cards
    if len(player_hand) == 2:
        if not is_soft:
            if total == 11: return "double"
            if total == 10 and dealer <= 9: return "double"
            if total == 9 and dealer in [3, 4, 5, 6]: return "double"
        else:
            if total in [19, 20, 21]: pass
            elif total == 18 and dealer in [3, 4, 5, 6]: return "double"
            elif total == 17 and dealer in [3, 4, 5, 6]: return "double"
            elif total in [15, 16] and dealer in [4, 5, 6]: return "double"
            elif total in [13, 14] and dealer in [5, 6]: return "double"

    # Hit or stand rules
    if is_soft:
        if total >= 19: return "stand"
        if total == 18:
            if dealer in [2, 7, 8]: return "stand"
            else: return "hit"
        return "hit"
    else:
        if total >= 17: return "stand"
        if 13 <= total <= 16:
            if dealer <= 6: return "stand"
            else: return "hit"
        if total == 12:
            if dealer in [4, 5, 6]: return "stand"
            else: return "hit"
        return "hit"

def execute_pure_gto_turn(deck, player_hand, dealer_upcard):
    action = get_gto_move(player_hand, dealer_upcard)
    
    if action == "split":
        hand1 = [player_hand[0], deck.pop()]
        hand2 = [player_hand[1], deck.pop()]
        results = []
        results.extend(execute_pure_gto_turn(deck, hand1, dealer_upcard))
        results.extend(execute_pure_gto_turn(deck, hand2, dealer_upcard))
        return results
        
    elif action == "double":
        player_hand.append(deck.pop())
        return [(player_hand, 2)]
        
    else:
        while get_gto_move(player_hand, dealer_upcard) == "hit":
            player_hand.append(deck.pop())
        return [(player_hand, 1)]