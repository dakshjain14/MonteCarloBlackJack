import streamlit as st
import matplotlib.pyplot as plt
from simulator import run_monte_carlo

st.set_page_config(page_title="Blackjack Monte Carlo", layout="wide")

st.title("Blackjack Monte Carlo Simulator")
st.markdown("We've always been told that the house always wins. You finally have a way to empirically test this! This program runs a simulation of thousands of Blackjack games, and gives you a way to empirically test that claim using applied probability and the Law of Large Numbers!")
st.sidebar.header("Simulation Settings")
num_hands = st.sidebar.slider("Number of Hands", min_value=100, max_value=100000, step=100, value=10000)
strategy = st.sidebar.selectbox("Player Strategy", ["Dealer Mimic", "Conservative"])

# Simple sidebar descriptions
if strategy == "Dealer Mimic":
    backend_strategy = "dealer_mimic"
    st.sidebar.info("**Dealer Mimic:** Player hits on 16 and below, stands on 17 and above.")
elif strategy == "Conservative":
    backend_strategy = "conservative"
    st.sidebar.info("**Conservative:** Player plays safe to avoid busting, standing on 15 and above.")

if st.sidebar.button("Run Simulation"):
    with st.spinner(f"Simulating {num_hands} hands..."):
        
        results = run_monte_carlo(num_hands, backend_strategy) 
        
        # Calculate House Edge percentage: (- net units / total hands) * 100
        house_edge = (-results['units_won'] / num_hands) * 100
        
        st.subheader("Final Statistics")
        # Expanded to 6 columns to include House Edge
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        col1.metric("Player Win Rate", f"{results['final_win_rate']:.2f}%")
        col2.metric("Player Wins", results['player_wins'])
        col3.metric("Dealer Wins", results['dealer_wins'])
        col4.metric("Pushes (Ties)", results['pushes'])
        col5.metric("Net Units", results['units_won'])
        col6.metric("House Edge", f"{house_edge:.2f}%")
        
        # Strategy analysis below stats
        st.subheader("Strategy Analysis")
        if backend_strategy == "dealer_mimic":
            st.info("**Dealer Mimic:** Even with identical rules, you lose because you must draw first. If you bust, you lose immediately, giving the casino the edge on mutual busts.")
        elif backend_strategy == "conservative":
            st.info("**Conservative:** Standing early on 15 avoids your own busts, but hands the advantage back to the dealer who simply draws to 17+ and beats you.")
        
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