import streamlit as st
import pandas as pd
import numpy as np
from prophet import Prophet
import matplotlib.pyplot as plt
from datetime import timedelta
import warnings
import os
warnings.filterwarnings("ignore")

st.set_page_config(page_title="MF Quant Engine", layout="wide")
st.title("Mutual Fund Quant & Forecasting")

@st.cache_data
def load_data():
    try:
        try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_path = os.path.join(current_dir, "clean_nav_data.parquet")
        
        # Load the data using the dynamic path
        df = pd.read_parquet(data_path)
        df['date'] = pd.to_datetime(df['date'])
        
        unique_funds = pd.Series(df["scheme_name"].unique())

        filter_keywords = [
            "FMP", "FIXED MATURITY", "FIXED TERM", "SERIES", "INTERVAL FUND",
            "CAPITAL PROTECTION", "CLOSED ENDED", "CLOSE ENDED", "CLOSE-ENDED",
            "CAP PROTECTION", "LIMITED OFFER", "NFO", "MATURITY", "TARGET MATURITY",
            "SEGREGATED PORTFOLIO", "LOCK-IN", "LIMITED PERIOD",
            "OVERNIGHT", "LIQUID", "ULTRA SHORT", "ULTRA-SHORT", "MONEY MARKET",
            "GILT", "ARBITRAGE", "SHORT DURATION", "LOW DURATION", "CORPORATE BOND",
            "CREDIT RISK", "DYNAMIC BOND", "BANKING AND PSU", "ETF"
        ]

        keyword_pattern = "|".join(filter_keywords)
        valid_fund_names = unique_funds[
            ~unique_funds.str.contains(keyword_pattern, case=False, na=False)
        ]

        fund_counts = df["scheme_name"].value_counts()
        mature_funds = fund_counts[fund_counts > 400].index

        final_valid_funds = set(valid_fund_names).intersection(set(mature_funds))
        df = df[df["scheme_name"].isin(final_valid_funds)]

        return df

    except FileNotFoundError:
        st.error("Data file missing. Run the local pipeline first.")
        st.stop()


df = load_data()
funds_list = sorted(df["scheme_name"].unique())

tab1, tab2, tab3 = st.tabs(
    ["Recommendations", "Prophet Forecast", "Strategy Backtest"]
)


with tab1:
    st.subheader("Fund Recommendations")

    @st.cache_data
    def precompute_fund_stats(data):
        latest_date = data["date"].max()
        one_year_ago = latest_date - pd.DateOffset(years=1)

        recent_data = data[data["date"] >= one_year_ago].copy()
        recent_data["return"] = recent_data.groupby("scheme_name")["nav"].pct_change()

        metrics = recent_data.groupby("scheme_name").agg(
            current_nav=("nav", "last"),
            start_nav=("nav", "first"),
            daily_mean=("return", "mean"),
            daily_std=("return", "std"),
        ).reset_index()

        metrics["Expected Annual Return (%)"] = metrics["daily_mean"] * 252 * 100
        metrics["Annualized Volatility (%)"] = metrics["daily_std"] * np.sqrt(252) * 100

        risk_free = (1.04 ** (1 / 252)) - 1
        metrics["Sharpe Ratio"] = (
            (metrics["daily_mean"] - risk_free) / metrics["daily_std"] * np.sqrt(252)
        )

        age_proxy = data.groupby("scheme_name").size() / 252
        metrics = metrics.merge(age_proxy.rename("Fund Age (Yrs)"), on="scheme_name")

        return metrics.dropna()

    master_stats_df = precompute_fund_stats(df)

    col1, col2 = st.columns(2)

    with col1:
        horizon_years = st.slider(
            "Investment Horizon (Years)", min_value=1, max_value=10, value=5
        )

    with col2:
        risk_profile = st.selectbox(
            "Risk Tolerance", ["Low", "Medium", "High"], index=2
        )

    def apply_suitability_score(metrics_df, horizon, risk):
        scored_df = metrics_df.copy()

        exp_return_norm = np.clip(
            scored_df["Expected Annual Return (%)"] / 50, 0, 1
        )
        sharpe_norm = np.clip(scored_df["Sharpe Ratio"] / 3, 0, 1)
        volatility_norm = np.clip(
            1 - (scored_df["Annualized Volatility (%)"] / 50), 0, 1
        )

        if risk == "Low":
            score = (
                (sharpe_norm * 0.6)
                + (volatility_norm * 0.3)
                + (exp_return_norm * 0.1)
            )
        elif risk == "Medium":
            score = (
                (exp_return_norm * 0.4)
                + (sharpe_norm * 0.4)
                + (volatility_norm * 0.2)
            )
        else:
            score = (
                (exp_return_norm * 0.7)
                + (sharpe_norm * 0.2)
                + (volatility_norm * 0.1)
            )

        horizon_mask = scored_df["Fund Age (Yrs)"] > horizon
        score = np.where(horizon_mask, score * 1.1, score)

        scored_df["Suitability Score"] = score * 100
        return scored_df.sort_values("Suitability Score", ascending=False)

    if st.button("Generate Portfolio"):
        recs = apply_suitability_score(
            master_stats_df, horizon_years, risk_profile
        )

        display_cols = [
            "scheme_name",
            "Suitability Score",
            "Expected Annual Return (%)",
            "Annualized Volatility (%)",
            "Sharpe Ratio",
        ]

        st.dataframe(recs[display_cols].head(15), use_container_width=True)


with tab2:
    st.subheader("NAV Forecast")

    selected_fund_forecast = st.selectbox(
        "Select Fund", funds_list, key="forecast_fund"
    )

    if st.button("Generate 1-Year Forecast"):
        fund_df = df[df["scheme_name"] == selected_fund_forecast][
            ["date", "nav"]
        ].copy()

        fund_df = fund_df.sort_values("date").drop_duplicates(
            "date", keep="last"
        )

        if len(fund_df) < 365:
            st.warning("Need at least 365 days of history.")
        else:
            with st.spinner("Training model..."):
                prophet_df = fund_df.rename(
                    columns={"date": "ds", "nav": "y"}
                )

                m = Prophet(
                    daily_seasonality=False,
                    yearly_seasonality=True,
                )

                m.fit(prophet_df)

                future = m.make_future_dataframe(periods=365)
                forecast = m.predict(future)

                fig = m.plot(
                    forecast,
                    xlabel="Date",
                    ylabel="NAV",
                )

                plt.title(selected_fund_forecast)
                st.pyplot(fig)


with tab3:
    st.subheader("Strategy Backtest")

    selected_fund_bt = st.selectbox(
        "Select Fund", funds_list, key="bt_fund"
    )

    if st.button("Run Backtest"):
        with st.spinner("Running strategy..."):
            fund_df = df[df["scheme_name"] == selected_fund_bt].copy()

            fund_df = fund_df.sort_values("date").drop_duplicates(
                "date", keep="last"
            )

            fund_df["ema_fast"] = fund_df["nav"].ewm(
                span=20, adjust=False
            ).mean()

            fund_df["ema_slow"] = fund_df["nav"].ewm(
                span=50, adjust=False
            ).mean()

            split_date = fund_df["date"].max() - timedelta(days=365)

            train_df = fund_df[fund_df["date"] <= split_date]
            test_df = fund_df[fund_df["date"] > split_date].copy()

            model_df = train_df[["date", "nav"]].rename(
                columns={"date": "ds", "nav": "y"}
            )

            m = Prophet(daily_seasonality=False)
            m.fit(model_df)

            forecast = m.predict(
                m.make_future_dataframe(periods=len(test_df))
            )

            test_df = test_df.merge(
                forecast[["ds", "yhat"]],
                left_on="date",
                right_on="ds",
            )

            test_df["signal"] = 0
            test_df.loc[
                (test_df["ema_fast"] > test_df["ema_slow"])
                & (test_df["yhat"] > test_df["nav"] * 0.98),
                "signal",
            ] = 1

            test_df["daily_ret"] = test_df["nav"].pct_change().fillna(0)

            test_df["bench_cum"] = (
                (1 + test_df["daily_ret"]).cumprod() - 1
            )

            test_df["strat_ret"] = (
                test_df["daily_ret"]
                * test_df["signal"].shift(1).fillna(0)
            )

            test_df["strat_cum"] = (
                (1 + test_df["strat_ret"]).cumprod() - 1
            )

            strat_return = test_df["strat_cum"].iloc[-1] * 100
            bench_return = test_df["bench_cum"].iloc[-1] * 100

            col1, col2 = st.columns(2)

            col1.metric("Strategy Return", f"{strat_return:.2f}%")
            col2.metric("Buy & Hold Return", f"{bench_return:.2f}%")

            st.line_chart(
                test_df.set_index("date")[["bench_cum", "strat_cum"]]
            )
