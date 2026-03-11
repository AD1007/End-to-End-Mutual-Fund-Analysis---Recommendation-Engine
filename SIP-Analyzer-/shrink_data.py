import pandas as pd
import numpy as np

print("Loading data...")
df = pd.read_parquet("final_nav_data.parquet")

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

df_clean = df[df["scheme_name"].isin(final_valid_funds)].copy()

df_clean["nav"] = df_clean["nav"].astype("float32")

print(f"Original Rows: {len(df)} | Clean Rows: {len(df_clean)}")

print("Saving parquet file...")
df_clean.to_parquet("clean_nav_data.parquet", compression="brotli")

print("Finished. File: clean_nav_data.parquet")
