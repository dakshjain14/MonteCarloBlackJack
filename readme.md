# Blackjack Monte Carlo Simulator
We've always been told that the house always wins. This app runs thousands of simulated Blackjack hands so you can empirically test that claim using applied probability and the Law of Large Numbers.

## Features
- Simulates anywhere from 100 to 100,000 hands of Blackjack in seconds.
- Three distinct player strategies to test and compare: Aggressive (mimics the dealer, splits all pairs, doubles on 9–11), Conservative (stands on 15+, avoids splitting to lower variance, only doubles on 11), and Pure GTO (uses an exact Basic Strategy decision matrix based on the dealer's upcard).
- Tracks full game mechanics including natural 3:2 Blackjack payouts, soft/hard Ace adjustments, pair splitting, and doubling down.
- Calculates final win rates, pushes, net units won, and the exact house edge percentage.
- Plots win rate convergence over time to visually demonstrate the Law of Large Numbers.

## Built with
Python
Streamlit
Matplotlib

## Try it

https://montecarloblackjack.streamlit.app/

## Running locally
```bash
git clone [https://github.com/dakshjain14/MonteCarloBlackJack](https://github.com/dakshjain14/MonteCarloBlackJack)
cd MonteCarloBlackJack
pip install -r requirements.txt
streamlit run dashboard.py