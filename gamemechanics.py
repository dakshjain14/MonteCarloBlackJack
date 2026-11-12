from dataclasses import dataclass
import random
from typing import List, Optional, Sequence, Tuple


RANKS = ("2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A")
SUITS = ("♠", "♥", "♦", "♣")


@dataclass(frozen=True)
class Card:
    rank: str
    suit: str

    @property
    def value(self) -> int:
        if self.rank == "A":
            return 11
        if self.rank in ("J", "Q", "K"):
            return 10
        return int(self.rank)

    def __str__(self) -> str:
        return f"{self.rank}{self.suit}"


@dataclass(frozen=True)
class BlackjackRules:
    decks: int = 6
    dealer_hits_soft_17: bool = False
    blackjack_payout: float = 1.5
    double_after_split: bool = True
    max_hands: int = 4
    resplit_aces: bool = False
    cut_card_fraction: float = 0.25

    def __post_init__(self) -> None:
        if self.decks < 1:
            raise ValueError("decks must be at least 1")
        if self.max_hands < 1:
            raise ValueError("max_hands must be at least 1")
        if not 0 < self.cut_card_fraction < 1:
            raise ValueError("cut_card_fraction must be between 0 and 1")
        if self.blackjack_payout <= 0:
            raise ValueError("blackjack_payout must be positive")


@dataclass
class PlayerHand:
    cards: List[Card]
    bet: float = 1.0
    is_split: bool = False
    split_aces: bool = False


class Shoe:
    def __init__(self, rules: BlackjackRules, rng: Optional[random.Random] = None):
        self.rules = rules
        self.rng = rng or random.Random()
        self.full_size = 52 * rules.decks
        self.cut_card = int(self.full_size * rules.cut_card_fraction)
        self.cards: List[Card] = []
        self.shuffle_number = 0
        self.shuffle()

    def shuffle(self) -> None:
        self.cards = deck_creation(self.rules.decks, self.rng)
        self.shuffle_number += 1

    def prepare_for_round(self) -> None:
        if len(self.cards) < self.cut_card:
            self.shuffle()

    def draw(self) -> Card:
        if not self.cards:
            raise RuntimeError("The shoe ran out of cards during a round")
        return self.cards.pop()


def deck_creation(num_decks: int = 6, rng: Optional[random.Random] = None) -> List[Card]:
    if num_decks < 1:
        raise ValueError("num_decks must be at least 1")
    generator = rng or random.Random()
    deck = [Card(rank, suit) for _ in range(num_decks) for suit in SUITS for rank in RANKS]
    generator.shuffle(deck)
    return deck


def hand_value(hand: Sequence[Card]) -> Tuple[int, bool]:
    total = sum(card.value for card in hand)
    aces = sum(card.rank == "A" for card in hand)

    while total > 21 and aces:
        total -= 10
        aces -= 1

    return total, aces > 0


def hand_total(hand: Sequence[Card]) -> int:
    return hand_value(hand)[0]


def is_blackjack(hand: Sequence[Card], is_split: bool = False) -> bool:
    return not is_split and len(hand) == 2 and hand_total(hand) == 21


def dealer_turn(shoe: Shoe, dealer_hand: List[Card], rules: BlackjackRules) -> List[Card]:
    while True:
        total, is_soft = hand_value(dealer_hand)
        if total < 17 or (total == 17 and is_soft and rules.dealer_hits_soft_17):
            dealer_hand.append(shoe.draw())
        else:
            return dealer_hand


def can_split(hand: PlayerHand, hands_created: int, rules: BlackjackRules) -> bool:
    if len(hand.cards) != 2 or hands_created >= rules.max_hands:
        return False
    if hand.cards[0].rank != hand.cards[1].rank:
        return False
    if hand.split_aces and not rules.resplit_aces:
        return False
    return True


def can_double(hand: PlayerHand, rules: BlackjackRules) -> bool:
    if len(hand.cards) != 2 or hand.split_aces:
        return False
    if hand.is_split and not rules.double_after_split:
        return False
    return True


def settle_hand(player_hand: PlayerHand, dealer_total: int) -> Tuple[str, float]:
    player_total = hand_total(player_hand.cards)

    if player_total > 21:
        return "loss", -player_hand.bet
    if dealer_total > 21 or player_total > dealer_total:
        return "win", player_hand.bet
    if player_total < dealer_total:
        return "loss", -player_hand.bet
    return "push", 0.0
