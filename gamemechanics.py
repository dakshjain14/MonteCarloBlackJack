import random
def deck_creation():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] 
    #Every ace is 11 by default, only 1 in the case of bust
    deck = cards*4
    random.shuffle(deck)
    return deck

def hand_total(hand):
    total = sum(hand)
    aces = hand.count(11) #Gives us number of aces
    while total > 21 and aces>0:
        total-=10
        aces-=1
    #Efficiently handles the case of aces being 1 instead of 11
    return total

def dealer_turn(deck, dealer_hand):
    #Dealer hits on 16 and lower, stands on 17 and above
    while hand_total(dealer_hand) < 17:
        dealer_hand.append(deck.pop()) #Deck.pop removes the top card
    return dealer_hand


#The two following strategies are "bad" strategies. They serve to show how big of an edge the casino possesses against a regular player (non-GTO).
def player_turn(deck, player_hand, strategy="dealer_mimic"):
    if strategy == "dealer_mimic": #It is named dealer mimic since the player hits on all 16s
        while hand_total(player_hand) < 17:
            player_hand.append(deck.pop())
            
    elif strategy == "conservative": #The player stands on all 16s
        while hand_total(player_hand) < 15:
            player_hand.append(deck.pop())
            
    return player_hand

# --- Terminal Test ---
if __name__ == "__main__":
    test_deck = deck_creation()
    d_hand = [test_deck.pop(), test_deck.pop()] #pops two cards from the deck and places them into the dealer's hand
    print(f"Dealer starting hand: {d_hand} (Total: {hand_total(d_hand)})")
    d_final = dealer_turn(test_deck, d_hand)
    print(f"Dealer final hand: {d_final} (Final Total: {hand_total(d_final)})\n")