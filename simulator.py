import random
from math import sqrt
from typing import Dict, Optional

from gamemechanics import (
    BlackjackRules,
    PlayerHand,
    Shoe,
    dealer_turn,
    hand_total,
    is_blackjack,
    settle_hand,
)
from strategy import get_strategy_move, validate_basic_strategy_rules


def play_player_hands(
    shoe: Shoe,
    starting_hand,
    dealer_upcard,
    strategy: str,
    rules: BlackjackRules,
):
    pending = [PlayerHand(list(starting_hand))]
    finished = []
    hands_created = 1
    extra_wager = 0.0

    while pending:
        hand = pending.pop(0)
        total = hand_total(hand.cards)

        if total >= 21:
            finished.append(hand)
            continue

        # Split aces get one card. Re-splitting is a separate table option.
        if hand.split_aces:
            is_pair_of_aces = (
                len(hand.cards) == 2
                and hand.cards[0].rank == "A"
                and hand.cards[1].rank == "A"
            )
            can_resplit = (
                rules.resplit_aces
                and is_pair_of_aces
                and hands_created < rules.max_hands
            )
            if not can_resplit:
                finished.append(hand)
                continue

        action = get_strategy_move(strategy, hand, dealer_upcard, rules, hands_created)

        if action == "split":
            first, second = hand.cards
            extra_wager += hand.bet
            hands_created += 1

            first_hand = PlayerHand(
                [first, shoe.draw()],
                bet=hand.bet,
                is_split=True,
                split_aces=(first.rank == "A"),
            )
            second_hand = PlayerHand(
                [second, shoe.draw()],
                bet=hand.bet,
                is_split=True,
                split_aces=(second.rank == "A"),
            )

            if first.rank == "A":
                # Split aces normally stop after their one draw.
                if rules.resplit_aces:
                    pending = [first_hand, second_hand] + pending
                else:
                    finished.extend((first_hand, second_hand))
            else:
                pending = [first_hand, second_hand] + pending
            continue

        if action == "double":
            extra_wager += hand.bet
            hand.bet *= 2
            hand.cards.append(shoe.draw())
            finished.append(hand)
            continue

        if action == "hit":
            hand.cards.append(shoe.draw())
            pending.insert(0, hand)
            continue

        finished.append(hand)

    return finished, extra_wager


def run_monte_carlo(
    num_rounds: int,
    strategy: str = "basic_strategy",
    seed: Optional[int] = None,
    rules: Optional[BlackjackRules] = None,
) -> Dict[str, object]:
    if num_rounds < 1:
        raise ValueError("num_rounds must be at least 1")

    rules = rules or BlackjackRules()
    if strategy == "basic_strategy":
        validate_basic_strategy_rules(rules)
    rng = random.Random(seed)
    shoe = Shoe(rules, rng)

    hand_wins = 0
    hand_losses = 0
    hand_pushes = 0
    round_positive = 0
    round_negative = 0
    round_zero = 0
    net_units_won = 0.0
    total_wagered = 0.0
    cumulative_player_return = []
    cumulative_sum = 0.0
    current_shoe_number = shoe.shuffle_number
    shoe_profit = 0.0
    shoe_rounds = 0
    shoe_results = []

    for round_number in range(1, num_rounds + 1):
        shoe.prepare_for_round()
        if shoe.shuffle_number != current_shoe_number:
            if shoe_rounds:
                shoe_results.append((shoe_profit, shoe_rounds))
            current_shoe_number = shoe.shuffle_number
            shoe_profit = 0.0
            shoe_rounds = 0
        total_wagered += 1.0

        # Deal in normal player-dealer-player-dealer order.
        player_hand = [shoe.draw()]
        dealer_hand = [shoe.draw()]
        player_hand.append(shoe.draw())
        dealer_hand.append(shoe.draw())
        dealer_upcard = dealer_hand[0]

        player_natural = is_blackjack(player_hand)
        dealer_natural = is_blackjack(dealer_hand)
        round_profit = 0.0

        if player_natural and dealer_natural:
            hand_pushes += 1
        elif dealer_natural:
            hand_losses += 1
            round_profit -= 1.0
        elif player_natural:
            hand_wins += 1
            round_profit += rules.blackjack_payout
        else:
            resolved_hands, extra_wager = play_player_hands(
                shoe, player_hand, dealer_upcard, strategy, rules
            )
            total_wagered += extra_wager

            # The dealer does not need to draw when every player hand has busted.
            if all(hand_total(hand.cards) > 21 for hand in resolved_hands):
                dealer_total = hand_total(dealer_hand)
            else:
                dealer_turn(shoe, dealer_hand, rules)
                dealer_total = hand_total(dealer_hand)

            for player_hand_result in resolved_hands:
                outcome, profit = settle_hand(player_hand_result, dealer_total)
                round_profit += profit
                if outcome == "win":
                    hand_wins += 1
                elif outcome == "loss":
                    hand_losses += 1
                else:
                    hand_pushes += 1

        net_units_won += round_profit
        cumulative_sum += round_profit
        shoe_profit += round_profit
        shoe_rounds += 1

        if round_profit > 1e-12:
            round_positive += 1
        elif round_profit < -1e-12:
            round_negative += 1
        else:
            round_zero += 1

        if round_number % 100 == 0 or round_number == num_rounds:
            cumulative_player_return.append(
                (round_number, cumulative_sum / round_number * 100)
            )

    if shoe_rounds:
        shoe_results.append((shoe_profit, shoe_rounds))

    hand_decisions = hand_wins + hand_losses
    hand_win_rate = hand_wins / hand_decisions * 100 if hand_decisions else 0.0
    round_positive_rate = round_positive / num_rounds * 100
    player_return_pct = net_units_won / num_rounds * 100
    house_edge_pct = -player_return_pct
    return_on_action_pct = -net_units_won / total_wagered * 100 if total_wagered else 0.0

    if len(shoe_results) >= 30:
        # Treat each shuffled shoe as a cluster; rounds within a shoe are dependent.
        average_profit = net_units_won / num_rounds
        residuals = [
            profit - average_profit * rounds for profit, rounds in shoe_results
        ]
        cluster_count = len(shoe_results)
        variance = (
            cluster_count / (cluster_count - 1)
            * sum(value * value for value in residuals)
            / (num_rounds * num_rounds)
        )
        standard_error_pct = sqrt(max(0.0, variance)) * 100
        player_return_ci = (
            player_return_pct - 1.96 * standard_error_pct,
            player_return_pct + 1.96 * standard_error_pct,
        )
        house_edge_ci = (-player_return_ci[1], -player_return_ci[0])
    else:
        player_return_ci = (float("nan"), float("nan"))
        house_edge_ci = (float("nan"), float("nan"))

    return {
        "rounds": num_rounds,
        "player_wins": hand_wins,
        "dealer_wins": hand_losses,
        "pushes": hand_pushes,
        "hand_wins": hand_wins,
        "hand_losses": hand_losses,
        "hand_pushes": hand_pushes,
        "hand_win_rate": hand_win_rate,
        "round_positive": round_positive,
        "round_negative": round_negative,
        "round_zero": round_zero,
        "round_positive_rate": round_positive_rate,
        "net_units_won": net_units_won,
        "units_won": net_units_won,
        "total_wagered": total_wagered,
        "player_return_pct": player_return_pct,
        "house_edge_pct": house_edge_pct,
        "return_on_total_action_pct": return_on_action_pct,
        "player_return_ci_95_pct": player_return_ci,
        "house_edge_ci_95_pct": house_edge_ci,
        "cumulative_player_return": cumulative_player_return,
        "seed": seed,
        "shoe_count": len(shoe_results),
        "strategy": strategy,
        "rules": rules,
    }


if __name__ == "__main__":
    results = run_monte_carlo(100_000, "basic_strategy", seed=42)
    print(f"Rounds: {results['rounds']:,}")
    print(f"Hand wins/losses/pushes: {results['hand_wins']:,} / "
          f"{results['hand_losses']:,} / {results['hand_pushes']:,}")
    print(f"Net units: {results['net_units_won']:.2f}")
    print(f"Total wagered: {results['total_wagered']:.2f}")
    print(f"Estimated house edge per initial bet: {results['house_edge_pct']:.3f}%")
