from gamemechanics import deck_creation, hand_total, dealer_turn, player_turn, is_blackjack

def run_monte_carlo(num_hands, strategy="dealer_mimic"):
    # This code plays hands of Blackjack using the strategy in gamemechanics.[cite: 5]
    # It tracks wins, losses to record the win rate over time to graph later.[cite: 5]

    player_wins = 0
    dealer_wins = 0
    pushes = 0
    
    # Tracking money for 3:2 blackjack payouts and split/double multipliers[cite: 5]
    units_won = 0.0

    # This array is used later to graph the Law of Large Numbers[cite: 5]
    win_rate_over_time = []

    for i in range(1, num_hands + 1):
        deck = deck_creation()
        player_hand = [deck.pop(), deck.pop()]
        dealer_hand = [deck.pop(), deck.pop()]
        
        # Check for natural Blackjacks before any turns are taken[cite: 5]
        player_has_bj = is_blackjack(player_hand)
        dealer_has_bj = is_blackjack(dealer_hand)
        
        if player_has_bj and dealer_has_bj:
            pushes += 1
        elif player_has_bj:
            player_wins += 1
            units_won += 1.5 # 3:2 payout[cite: 5]
        elif dealer_has_bj:
            dealer_wins += 1
            units_won -= 1.0
        else:
            # Player's turn: pass the dealer's upcard (first card) for GTO logic
            resolved_player_hands = player_turn(
                deck, 
                player_hand, 
                strategy=strategy, 
                dealer_upcard=dealer_hand[0]
            )
            
            # Dealer plays once for the round setup[cite: 5]
            dealer_hand = dealer_turn(deck, dealer_hand)
            d_total = hand_total(dealer_hand)
            
            # Evaluate each hand (handles splits turning 1 hand into multiple, or doubles)[cite: 5]
            for p_hand, multiplier in resolved_player_hands:
                p_total = hand_total(p_hand)
                
                if p_total > 21:
                    # Player busts[cite: 5]
                    dealer_wins += 1
                    units_won -= (1.0 * multiplier)
                elif d_total > 21:
                    # Dealer busts, player wins[cite: 5]
                    player_wins += 1
                    units_won += (1.0 * multiplier)
                elif p_total > d_total:
                    player_wins += 1
                    units_won += (1.0 * multiplier)
                elif d_total > p_total:
                    dealer_wins += 1
                    units_won -= (1.0 * multiplier)
                else:
                    pushes += 1
        
        # Data Tracking: Record the current win rate every 100 hands[cite: 5]
        if i % 100 == 0:
            total_resolved = player_wins + dealer_wins
            if total_resolved > 0:
                current_rate = (player_wins / total_resolved) * 100
                win_rate_over_time.append(current_rate)

    # Calculate final statistics[cite: 5]
    total_resolved = player_wins + dealer_wins
    final_win_rate = (player_wins / total_resolved) * 100 if total_resolved > 0 else 0
    
    return {
        "player_wins": player_wins,
        "dealer_wins": dealer_wins,
        "pushes": pushes,
        "units_won": units_won,
        "final_win_rate": final_win_rate,
        "win_rates": win_rate_over_time
    }

# --- Terminal Test ---
if __name__ == "__main__":
    test_hands = 10000
    print(f"Simulating {test_hands} hands with strategy...")
    
    results = run_monte_carlo(test_hands, "dealer_mimic")
    
    print("\n--- RESULTS ---")
    print(f"Final Win Rate: {results['final_win_rate']:.2f}%")
    print(f"Player Wins: {results['player_wins']}")
    print(f"Dealer Wins: {results['dealer_wins']}")
    print(f"Pushes: {results['pushes']}")
    print(f"Net Units Won: {results['units_won']}")