import matplotlib.pyplot as plt
import streamlit as st

from gamemechanics import BlackjackRules
from simulator import run_monte_carlo


st.set_page_config(page_title="Blackjack Monte Carlo", layout="wide")
st.title("Blackjack Monte Carlo Simulator")
st.write(
    "Test blackjack strategies with a multi-deck shoe, explicit table rules, "
    "and separate hand-level and round-level accounting. Results are estimates, "
    "not exact probabilities."
)

st.sidebar.header("Simulation settings")
num_rounds = st.sidebar.slider(
    "Starting rounds", min_value=100, max_value=100_000, step=100, value=10_000
)
strategy_label = st.sidebar.selectbox(
    "Player strategy", ["Basic Strategy", "Aggressive", "Conservative"]
)
strategy_map = {
    "Basic Strategy": "basic_strategy",
    "Aggressive": "aggressive",
    "Conservative": "conservative",
}
seed = st.sidebar.number_input("Random seed", min_value=0, value=42, step=1)
st.sidebar.caption("Use the same seed and settings to reproduce a run.")

rules = BlackjackRules()
st.sidebar.subheader("Table rules")
st.sidebar.write(
    "- 6 decks; reshuffle at 75% shoe penetration\n"
    "- Dealer stands on soft 17\n"
    "- Blackjack pays 3:2\n"
    "- Double on any first two cards\n"
    "- Double after split allowed\n"
    "- Up to 4 hands per round\n"
    "- Splits require the same rank\n"
    "- Split aces receive one card; no re-splitting aces\n"
    "- Dealer checks for blackjack before player decisions\n"
    "- No surrender or insurance"
)

if strategy_label == "Basic Strategy":
    st.sidebar.info(
        "Rule-matched basic strategy for this table. It is not a GTO solver."
    )
elif strategy_label == "Aggressive":
    st.sidebar.info(
        "Experimental heuristic: splits every eligible pair, doubles hard totals "
        "9–11, and otherwise hits below 17."
    )
else:
    st.sidebar.info(
        "Experimental heuristic: never splits, doubles 11, and stands on 15+."
    )

if st.button("Run simulation", type="primary"):
    with st.spinner(f"Simulating {num_rounds:,} starting rounds..."):
        results = run_monte_carlo(
            num_rounds=num_rounds,
            strategy=strategy_map[strategy_label],
            seed=int(seed),
            rules=rules,
        )

    st.subheader("Results")
    first_row = st.columns(4)
    first_row[0].metric("Starting rounds", f"{results['rounds']:,}")
    first_row[1].metric("Hand win rate", f"{results['hand_win_rate']:.2f}%")
    first_row[2].metric("Net units won", f"{results['net_units_won']:+,.2f}")
    first_row[3].metric("Total wagered", f"{results['total_wagered']:,.2f}")

    second_row = st.columns(4)
    second_row[0].metric("Hand wins", f"{results['hand_wins']:,}")
    second_row[1].metric("Hand losses", f"{results['hand_losses']:,}")
    second_row[2].metric("Hand pushes", f"{results['hand_pushes']:,}")
    second_row[3].metric("Positive-net rounds", f"{results['round_positive']:,}")

    third_row = st.columns(4)
    third_row[0].metric("Negative-net rounds", f"{results['round_negative']:,}")
    third_row[1].metric("Zero-net rounds", f"{results['round_zero']:,}")
    third_row[2].metric(
        "House edge / initial bet", f"{results['house_edge_pct']:+.3f}%"
    )
    third_row[3].metric(
        "House return / total action", f"{results['return_on_total_action_pct']:+.3f}%"
    )

    if results["shoe_count"] >= 30:
        low, high = results["house_edge_ci_95_pct"]
        st.caption(
            f"Approximate 95% interval for house edge per initial bet: "
            f"{low:+.3f}% to {high:+.3f}%. Calculated across "
            f"{results['shoe_count']:,} shuffled shoes; this is not a guarantee."
        )
    else:
        st.caption(
            f"Only {results['shoe_count']} shuffled shoes were used. "
            "Run more rounds for a useful uncertainty interval."
        )
    st.caption(
        "Hand stats count each split hand separately. Round stats combine all hands "
        "from the original deal: a winning split hand plus a losing split hand can "
        "be a zero-net round, but neither hand is counted as a push."
    )

    st.subheader("Return as the simulation grows")
    st.write(
        "The line shows cumulative player profit as a percentage of starting bets. "
        "It is more informative than win rate because it includes pushes, 3:2 "
        "blackjacks, splits, and doubles."
    )
    points = results["cumulative_player_return"]
    x_values = [point[0] for point in points]
    y_values = [point[1] for point in points]

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(x_values, y_values, linewidth=1.5, label="Cumulative player return")
    ax.axhline(y=0, linestyle="--", linewidth=1, label="Break-even")
    ax.set_xlabel("Starting rounds")
    ax.set_ylabel("Player return per initial bet (%)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)
    plt.close(fig)

    st.subheader("How to read the results")
    st.write(
        f"- **House edge:** {results['house_edge_pct']:+.3f}% is the estimated "
        "house advantage per original one-unit bet. A negative result means the "
        "player finished ahead in this sample.\n"
        f"- **Total action:** {results['total_wagered']:,.2f} units includes the "
        "extra stakes added by splits and doubles.\n"
        "- **Zero-net rounds:** these are not necessarily pushes. They can include "
        "a mix of wins and losses across split hands."
    )
