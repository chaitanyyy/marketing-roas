import numpy as np
import pandas as pd


def load():
    from src.config import get_engine
    return pd.read_sql("SELECT * FROM campaign_daily", get_engine(), parse_dates=["date"])


def fit_curves(df):
    """Fit revenue = a * spend^b per channel (log-log regression)."""
    rows = []
    for ch, d in df.groupby("channel"):
        d = d[(d.spend_inr > 0) & (d.revenue_inr > 0)]
        x, y = np.log(d.spend_inr.astype(float)), np.log(d.revenue_inr.astype(float))
        b, ln_a = np.polyfit(x, y, 1)
        a = np.exp(ln_a)
        s = d.spend_inr.astype(float).mean()
        r2 = 1 - (y - (ln_a + b * x)).var() / y.var()
        rows.append(dict(channel=ch, a=a, b=b, r2=r2, mean_daily_spend=s,
                         avg_roas=d.revenue_inr.sum() / d.spend_inr.sum(),
                         marginal_roas=a * b * s ** (b - 1)))      # return on the next rupee
    return pd.DataFrame(rows).set_index("channel")


if __name__ == "__main__":
    c = fit_curves(load())
    print(c[["b", "r2", "avg_roas", "marginal_roas"]].round(2).sort_values("avg_roas", ascending=False))
    c.to_csv("data/processed/response_curves.csv")