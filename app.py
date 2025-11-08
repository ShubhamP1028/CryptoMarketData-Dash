import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="Crypto Market Dashboard", layout="wide")

st.title("📊 Crypto Market Analytics Dashboard")
st.markdown("Real-time and historical market insights powered by CoinGecko API")

# --- Sidebar Controls ---
coins = ['bitcoin', 'ethereum', 'solana', 'cardano', 'dogecoin', 'polkadot']
selected_coins = st.multiselect("Select Cryptocurrencies:", coins, default=['bitcoin', 'ethereum'])
days = st.slider("Select Time Range (Days):", 30, 365, 90)
vs_currency = st.selectbox("Compare Against Currency:", ['usd', 'inr', 'eur'])

# --- Function to fetch historical data ---
@st.cache_data
def get_historical_data(coin, vs_currency='usd', days=90):
    url = f"https://api.coingecko.com/api/v3/coins/{coin}/market_chart"
    params = {'vs_currency': vs_currency, 'days': days}
    response = requests.get(url, params=params)
    data = response.json()
    df = pd.DataFrame(data['prices'], columns=['timestamp', 'price'])
    df['volume'] = [v[1] for v in data['total_volumes']]
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['coin'] = coin
    return df

# --- Fetch data for all selected coins ---
if st.button("🔍 Load Data"):
    all_data = pd.concat([get_historical_data(c, vs_currency, days) for c in selected_coins], ignore_index=True)
    st.success("Data loaded successfully!")

    # --- Plot Price Trends ---
    fig_price = px.line(
        all_data, x='timestamp', y='price', color='coin',
        title=f"Price Trends ({days} Days)"
    )
    st.plotly_chart(fig_price, use_container_width=True)

    # --- Plot Volume Trends ---
    fig_volume = px.line(
        all_data, x='timestamp', y='volume', color='coin',
        title=f"Trading Volume Trends ({days} Days)"
    )
    st.plotly_chart(fig_volume, use_container_width=True)

    # --- Analytics Section ---
    st.subheader("📈 Statistical Insights")
    all_data['daily_return'] = all_data.groupby('coin')['price'].pct_change()

    volatility = all_data.groupby('coin')['daily_return'].std().sort_values(ascending=False)
    st.write("**Volatility (Standard Deviation of Returns):**")
    st.dataframe(volatility)

    pivot_df = all_data.pivot(index='timestamp', columns='coin', values='price')
    corr = pivot_df.corr()
    st.write("**Price Correlation Between Coins:**")
    st.dataframe(corr)

    fig_corr = px.imshow(corr, text_auto=True, color_continuous_scale='Viridis', title="Correlation Heatmap")
    st.plotly_chart(fig_corr, use_container_width=True)

else:
    st.info("👆 Select coins and click 'Load Data' to begin.")
