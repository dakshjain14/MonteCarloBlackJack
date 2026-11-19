# Blackjack Monte Carlo Simulator

**▶ Live demo: https://dakshjain14.github.io/MonteCarloBlackJack/**
No installation needed. The simulator runs entirely in your browser.
The first load takes a few seconds while the Python runtime downloads.

"The house always wins" is a claim you can test. This project simulates blackjack
rounds from a shuffled multi-deck shoe under explicit table rules and estimates the
house edge for three player strategies, along with a statistical uncertainty interval.

## What it does

- Simulates 100 to 100,000 starting rounds from a 6-deck shoe with a cut card.
- Compares three strategies:
  - **Basic Strategy:** a decision chart matched to this table's rules
    (based on your total, whether it is soft, pairs, and the dealer's upcard).
    It is basic strategy, not a game-theory solver or card counting.
  - **Aggressive** (heuristic): splits every eligible pair, doubles on 9–11 with
    two cards, otherwise hits below 17.
  - **Conservative** (heuristic): never splits, doubles only on 11, stands on 15+.
- Models 3:2 blackjack payouts, soft/hard aces, splitting (up to 4 hands),
  doubling (including after splits), split-ace rules and the dealer peeking for blackjack.
- Reports results at two levels:
  - **Hand level:** each split hand counts as its own win, loss or push.
  - **Round level:** the net result of everything that happened after one initial deal.
- Estimates the **house edge per initial bet** and the **house return per total amount
  wagered**, with an approximate 95% confidence interval.
- Plots cumulative player return as the number of rounds grows.
- Runs are reproducible: the same seed and settings give the same result.

## Table rules

| Rule | Setting |
|---|---|
| Decks | 6, reshuffled at 75% penetration |
| Dealer soft 17 | Stands (S17) |
| Blackjack payout | 3:2 |
| Doubling | Any first two cards; double after split allowed |
| Splitting | Same rank only (e.g. K-K, not K-10); up to 4 hands |
| Split aces | One card each; no re-splitting |
| Dealer blackjack | Checked before the player acts |
| Surrender / insurance | Not offered |

## Methodology

**Simulation.** Each round deals player, dealer, player, dealer from a seeded,
shuffled shoe. The player's hands are played out according to the selected strategy.
The dealer then draws to 17 unless every player hand has already busted.

**Two edge measures.**
- *House edge per initial bet* = −(net units won) / (number of rounds).
  This is the figure normally quoted for blackjack.
- *House return per total action* = −(net units won) / (total units wagered,
  including split and double stakes).

**Uncertainty.** Rounds dealt from the same shoe are not independent, because they
share the same cards. The confidence interval therefore treats each shuffled shoe as
a cluster and uses a cluster-robust standard error. No interval is shown when fewer
than 30 shoes were used.

**How many rounds are enough?** One round's profit has a standard deviation of
about 1.15 units. At 100,000 rounds the standard error of the house edge is about
0.36%, so the 95% interval is roughly ±0.7%. That is wider than the house edge of
a good strategy, so a single run can't reliably separate Basic Strategy from break-even.
It can, however, show that the two heuristics do clearly worse. See *Limitations*.

## How it works

The site is static and hosted on GitHub Pages. No server runs any code.

```
Browser
 ├── index.html / style.css   page layout
 ├── app.js                   controls, results, chart (Chart.js)
 └── worker.js                background thread that loads Pyodide
       └── runs the unchanged Python engine:
           gamemechanics.py   cards, shoe, hand values, rules, settlement
           strategy.py        Basic