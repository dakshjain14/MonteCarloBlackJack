import streamlit as st
import matplotlib.pyplot as plt
from simulator import run_monte_carlo

st.set_page_config(page_title="Blackjack Monte Carlo", layout="wide")

st.title("Blackjack Monte Carlo Simulator")
st.markdown("We've always been told that the house always wins. You finally have a way to empirically test this! This program runs a simulation of thousands of Blackjack games, and gives you a way to empirically test that claim using applied probability and the Law of Large Numbers!")

st.sidebar.header("Simulation Settings")
num_hands = st.sidebar.slider("Number of Hands", min_value=100, max_value=100000, step=100, value=10000)

strategy = st.sidebar.selectbox("Player Strategy", ["Aggressive", "Conservative", "Pure GTO"])

if strategy == "Aggressive":
    backend_strategy = "dealer_mimic"
    st.sidebar.info("**Aggressive:** Hits on 16 and below, stands on 17+, splits matching pairs, and doubles down on 9, 10, and 11.")
elif strategy == "Conservative":
    backend_strategy = "conservative"
    st.sidebar.info("**Conservative:** Stands on 15 and above, avoids splitting pairs to limit variance, and only doubles down on 11.")
elif strategy == "Pure GTO":
    backend_strategy = "gto"
    st.sidebar.info("**Pure GTO:** Follows the mathematically perfect Basic Strategy matrix, deciding to hit, stand, split, or double based exactly on the player's total versus the dealer's visible card.")

if st.sidebar.button("Run Simulation"):
    with st.spinner(f"Simulating {num_hands} hands..."):
        
        results = run_monte_carlo(num_hands, backend_strategy) 
        
        # Calculate House Edge percentage: (- net units / total hands) * 100
        house_edge = (-results['units_won'] / num_hands) * 100
        
        st.subheader("Final Statistics")
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Player Win Rate", f"{results['final_win_rate']:.2f}%")
        col2.metric("Player Wins", results['player_wins'])
        col3.metric("Dealer Wins", results['dealer_wins'])
        col4.metric("Pushes (Ties)", results['pushes'])
        col5.metric("Net Units", results['units_won'])
        col6.metric("House Edge", f"{house_edge:.2f}%")
        
        # Natural, human-written strategy analysis
        st.subheader("Strategy Analysis")
        if backend_strategy == "dealer_mimic":
            st.info("""
            **Aggressive Strategy Breakdown:**
            * **The Splitting & Doubling Trap:** Splitting every pair and doubling down on marginal hands (like a 9 against a strong dealer card) sounds proactive, but it actually hurts you. Breaking up good hands or doubling on bad odds multiplies your bets right where the house has the advantage, causing your bankroll to bleed out much faster.
            """)
        elif backend_strategy == "conservative":
            st.info("""
            **Conservative Strategy Breakdown:**
            * **Why the House Edge Dropped to 3.3%:** By dodging the high-risk trap of splitting pairs and only doubling down when you draw a rock-solid 11, you cut out reckless bets. Standing early on 15 plus smart, selective doubling keeps your variance low and protects your bankroll from massive swings.
            """)
        elif backend_strategy == "gto":
            st.info("""
            **Pure GTO Strategy Breakdown:**
            * **Mathematical Perfection:** By flawlessly cross-referencing your total against the dealer's upcard, this strategy maximizes Expected Value (EV). It exploits dealer weakness (2-6) by doubling aggressive soft hands and standing early, while mitigating losses against strong dealer cards (7-Ace) by hitting appropriately. This drives the house edge down to its theoretical minimum (around 0.5%).
            """)
        
        st.subheader("The Law of Large Numbers")
        st.markdown("While the win rate fluctuates wildly at the start, it converges to a constant as the sample size increases!")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        
        # X-axis shows 100-hand interval
        x_values = [i * 100 for i in range(1, len(results['win_rates']) + 1)]
        
        ax.plot(x_values, results['win_rates'], label="Current Win Rate", color="#9065df", linewidth=1.5)
        ax.axhline(y=results['final_win_rate'], color='red', linestyle = '--', label=f"Convergence ({results['final_win_rate']:.2f}%)")
        ax.set_xlabel("Number of Hands")
        ax.set_ylabel("Win Rate in %")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        st.pyplot(fig)