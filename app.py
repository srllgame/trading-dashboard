
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# Page config
st.set_page_config(page_title="TraderSync Clone Dashboard", layout="wide", initial_sidebar_state="expanded")
st.markdown("""
    <style>
        body {
            background-color: #1e1e1e;
            color: white;
        }
        .css-18e3th9 {
            background-color: #1e1e1e;
        }
        .css-1d391kg, .css-1v3fvcr, .css-1cpxqw2 {
            background-color: #2e2e2e;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

# Upload file
st.sidebar.title("📁 Upload Your Data")
uploaded_file = st.sidebar.file_uploader("Upload your closedPositionsTab.csv", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df['Close time'] = pd.to_datetime(df['Close time'])
    df['Open time'] = pd.to_datetime(df['Open time'])
    df['Date'] = df['Close time'].dt.date
    df['Hour'] = df['Open time'].dt.hour
    df['Weekday'] = df['Open time'].dt.day_name()

    # Auto-label win/loss and side
    df['Result'] = df['Profit'].apply(lambda x: 'WIN' if x > 0 else 'LOSS')
    df['Side'] = df['Side'].str.upper()
    df['Setup'] = np.where(df['Profit'] > 200, 'Gap Up', np.where(df['Profit'] < -200, 'Reversal', 'Standard'))

    # Filters
    st.sidebar.subheader("🔎 Filters")
    symbols = st.sidebar.multiselect("Symbol", sorted(df['Symbol'].unique()), default=list(df['Symbol'].unique()))
    setups = st.sidebar.multiselect("Setup", sorted(df['Setup'].unique()), default=list(df['Setup'].unique()))
    sides = st.sidebar.multiselect("Side", sorted(df['Side'].unique()), default=list(df['Side'].unique()))
    weekdays = st.sidebar.multiselect("Weekday", sorted(df['Weekday'].unique()), default=list(df['Weekday'].unique()))

    df = df[df['Symbol'].isin(symbols) & df['Setup'].isin(setups) & df['Side'].isin(sides) & df['Weekday'].isin(weekdays)]

    # Risk limits
    daily_limit = -1500
    total_limit = -2500
    risk_per_trade = 100

    # Summary stats
    total_pnl = df['Profit'].sum()
    avg_return = df['Profit'].mean()
    win_rate = (df['Profit'] > 0).mean() * 100

    st.title("💹 TraderSync-Style Dashboard")
    st.markdown("---")

    # Daily drawdown check
    daily_pnl = df.groupby("Date")["Profit"].sum().reset_index()
    daily_pnl['Breach'] = daily_pnl['Profit'] < daily_limit

    if any(daily_pnl['Breach']):
        st.error("🚨 WARNING: You breached the daily drawdown limit on one or more days!")

    if total_pnl <= total_limit:
        st.error("❌ MAX ACCOUNT DRAWDOWN BREACHED. Stop trading!")

    # Highlight trades over $100 loss
    df['Risk Violation'] = df['Profit'] < -risk_per_trade
    violations = df[df['Risk Violation'] == True]
    if not violations.empty:
        st.warning(f"⚠️ {len(violations)} trades exceeded your $100 per-trade risk limit.")
        st.dataframe(violations[["Date", "Symbol", "Side", "Profit", "Setup"]])

    col1, col2, col3 = st.columns(3)
    col1.metric("Total PnL", f"${total_pnl:,.2f}")
    col2.metric("Win Rate", f"{win_rate:.1f}%")
    col3.metric("Avg Return", f"${avg_return:,.2f}")

    # Cumulative PnL chart
    df_sorted = df.sort_values("Close time")
    df_sorted["Cumulative PnL"] = df_sorted["Profit"].cumsum()
    fig_cum = px.line(df_sorted, x="Close time", y="Cumulative PnL", title="Cumulative PnL Over Time")
    st.plotly_chart(fig_cum, use_container_width=True)

    # Profit by symbol
    symbol_group = df.groupby("Symbol")["Profit"].sum().reset_index().sort_values(by="Profit", ascending=False)
    fig_symbol = px.bar(symbol_group, x="Symbol", y="Profit", title="Profit by Symbol", color="Profit",
                        color_continuous_scale="Bluered")
    st.plotly_chart(fig_symbol, use_container_width=True)

    # Win rate donut
    win_counts = df['Result'].value_counts()
    fig_donut = go.Figure(data=[
        go.Pie(labels=win_counts.index, values=win_counts.values, hole=.6)
    ])
    fig_donut.update_layout(title_text="Win/Loss Ratio")
    st.plotly_chart(fig_donut, use_container_width=True)

    # Hourly performance
    hourly_perf = df.groupby('Hour')["Profit"].sum().reset_index()
    fig_hour = px.bar(hourly_perf, x="Hour", y="Profit", title="Hourly Profitability")
    st.plotly_chart(fig_hour, use_container_width=True)

    # Weekday x Hour Heatmap
    st.subheader("🧭 Trade Timing Heatmap")
    heatmap_data = df.groupby(['Weekday', 'Hour'])["Profit"].sum().reset_index()
    heatmap_pivot = heatmap_data.pivot(index="Weekday", columns="Hour", values="Profit").fillna(0)
    heatmap_pivot = heatmap_pivot.loc[["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]]  # Keep weekday order
    fig_heatmap = px.imshow(
        heatmap_pivot,
        color_continuous_scale='RdYlGn',
        labels=dict(x="Hour", y="Weekday", color="Profit ($)"),
        title="Profit Heatmap by Weekday and Hour"
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

    # Setup performance
    st.subheader("📊 Setup Performance")
    setup_stats = df.groupby("Setup").agg(
        Trades=("ID", "count"),
        WinRate=("Result", lambda x: (x == "WIN").mean() * 100),
        AvgReturn=("Profit", "mean"),
        TotalProfit=("Profit", "sum")
    ).reset_index().sort_values(by="TotalProfit", ascending=False)
    st.dataframe(setup_stats.round(2))

    fig_setup = px.bar(setup_stats, x="TotalProfit", y="Setup", orientation='h',
                       title="Total Profit by Setup", color="WinRate",
                       color_continuous_scale="greens")
    st.plotly_chart(fig_setup, use_container_width=True)

    # Trade table
    st.subheader("📋 Trade Log")
    display_df = df[["Date", "Symbol", "Open price", "Close Price", "Side", "Profit", "Result", "Setup"]]
    st.dataframe(display_df.style.applymap(
        lambda v: 'color: lime;' if v == 'WIN' else ('color: red;' if v == 'LOSS' else None), subset=['Result'])
    )
