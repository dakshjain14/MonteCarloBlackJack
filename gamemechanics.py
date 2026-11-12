import random
from gto_strategy import execute_pure_gto_turn # Add this import

def deck_creation():
    cards = [2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10, 11] 
    deck = cards * 4
    random.shuffle(deck)
    return deck

def hand_total(hand):
    total = sum(hand)
    aces = hand.count(11)
    while total > 21 and aces > 0:
        total -= 10
        aces -= 1
    return total

def is_blackjack(hand):
    return len(hand) == 2 and hand_total(hand) == 21

def dealer_turn(deck, dealer_hand):
    while hand_total(dealer_hand) < 17:
        dealer_hand.append(deck.pop())
    return dealer_hand

# Add dealer_upcard=None to the parameters
def player_turn(deck, player_hand, strategy="dealer_mimic", dealer_upcard=None):
    # Add the GTO routing first
    if strategy == "gto":
        return execute_pure_gto_turn(deck, player_hand, dealer_upcard)
        
    if strategy == "dealer_mimic": 
        if len(player_hand) == 2 and player_hand[0] == player_hand[1]:
            hand1 = [player_hand[0], deck.pop()]
            hand2 = [player_hand[1], deck.pop()]
            results = []
            results.extend(player_turn(deck, hand1, "dealer_mimic"))
            results.extend(player_turn(deck, hand2, "dealer_mimic"))
            return results

        multiplier = 1
        total = hand_total(player_hand)
        
        if len(player_hand) == 2 and total in [9, 10, 11]:
            multiplier = 2
            player_hand.append(deck.pop())
        else:
            while hand_total(player_hand) < 17:
                player_hand.append(deck.pop())
                
        return [(player_hand, multiplier)]
        
    elif strategy == "conservative": 
        multiplier = 1
        total = hand_total(player_hand)
        
        if len(player_hand) == 2 and total == 11:
            multiplier = 2
            player_hand.append(deck.pop())
        else:
            while hand_total(player_hand) < 15:
                player_hand.append(deck.pop())
                
        return [(player_hand, multiplier)]
        
    return [(player_hand, 1)]