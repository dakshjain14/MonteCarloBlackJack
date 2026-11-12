from gamemechanics import BlackjackRules, PlayerHand, can_double, can_split, hand_value


def validate_basic_strategy_rules(rules: BlackjackRules) -> None:
    expected = (
        rules.decks == 6
        and not rules.dealer_hits_soft_17
        and rules.blackjack_payout == 1.5
        and rules.double_after_split
        and rules.max_hands == 4
        and not rules.resplit_aces
    )
    if not expected:
        raise ValueError(
            "The Basic Strategy chart is for 6 decks, S17, 3:2 blackjack, "
            "DAS, a four-hand limit, and no re-splitting aces."
        )


# Six decks, dealer stands on soft 17, double after split, no surrender.
# H = hit, S = stand, D = double, P = split.

PAIR_SPLITS = {
    "2": {2, 3, 4, 5, 6, 7},
    "3": {2, 3, 4, 5, 6, 7},
    "4": {5, 6},
    "6": {2, 3, 4, 5, 6},
    "7": {2, 3, 4, 5, 6, 7},
    "8": {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
    "9": {2, 3, 4, 5, 6, 8, 9},
    "A": {2, 3, 4, 5, 6, 7, 8, 9, 10, 11},
}


def get_basic_strategy_move(
    hand: PlayerHand,
    dealer_upcard,
    rules: BlackjackRules,
    hands_created: int,
) -> str:
    validate_basic_strategy_rules(rules)
    cards = hand.cards
    dealer = dealer_upcard.value
    total, is_soft = hand_value(cards)
    double_allowed = can_double(hand, rules)
    split_allowed = can_split(hand, hands_created, rules)

    # Split decisions come before hard totals.
    if len(cards) == 2 and cards[0].rank == cards[1].rank and split_allowed:
        pair = cards[0].rank
        if pair in PAIR_SPLITS and dealer in PAIR_SPLITS[pair]:
            return "split"

    # A split ace gets one card, unless the table allows re-splitting aces.
    if hand.split_aces:
        return "stand"

    if is_soft:
        if total <= 14:
            should_double = total in (13, 14) and dealer in (5, 6)
        elif total in (15, 16):
            should_double = dealer in (4, 5, 6)
        elif total == 17:
            should_double = dealer in (3, 4, 5, 6)
        elif total == 18:
            if dealer in (2, 3, 4, 5, 6):
                return "double" if double_allowed else "stand"
            if dealer in (7, 8):
                return "stand"
            return "hit"
        else:
            return "stand"

        if should_double:
            return "double" if double_allowed else "hit"
        return "hit"

    if total == 9:
        return "double" if dealer in (3, 4, 5, 6) and double_allowed else "hit"
    if total == 10:
        return "double" if dealer <= 9 and double_allowed else "hit"
    if total == 11:
        return "double" if dealer <= 10 and double_allowed else "hit"
    if total == 12:
        return "stand" if dealer in (4, 5, 6) else "hit"
    if 13 <= total <= 16:
        return "stand" if dealer <= 6 else "hit"
    if total >= 17:
        return "stand"
    return "hit"


def get_strategy_move(
    strategy: str,
    hand: PlayerHand,
    dealer_upcard,
    rules: BlackjackRules,
    hands_created: int,
) -> str:
    if strategy == "basic_strategy":
        return get_basic_strategy_move(hand, dealer_upcard, rules, hands_created)

    total, _ = hand_value(hand.cards)
    double_allowed = can_double(hand, rules)
    split_allowed = can_split(hand, hands_created, rules)

    if strategy == "aggressive":
        if split_allowed:
            return "split"
        if len(hand.cards) == 2 and 9 <= total <= 11 and double_allowed:
            return "double"
        return "hit" if total < 17 else "stand"

    if strategy == "conservative":
        if len(hand.cards) == 2 and total == 11 and double_allowed:
            return "double"
        return "hit" if total < 15 else "stand"

    raise ValueError(f"Unknown strategy: {strategy}")
