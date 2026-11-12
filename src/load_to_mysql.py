import pandas as pd
from sqlalchemy import text
from src.config import get_engine

engine = get_engine()
files = {
    "campaign_daily": "data/raw/p3_campaign_daily.csv",
    "channel_assumptions": "data/raw/p3_channel_assumptions.csv",
    "ab_test": "data/raw/p3_ab_test.csv",
}
with engine.begin() as conn:
    for t in files:
        conn.execute(text(f"DELETE FROM {t}"))
for t, f in files.items():
    pd.read_csv(f).to_sql(t, engine, if_exists="append", index=False)

with engine.connect() as conn:
    for t in files:
        print(t, conn.execute(text(f"SELECT COUNT(*) FROM {t}")).scalar())