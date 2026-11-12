"""Generate SYNTHETIC marketing data (6 ad channels, 92 days) + landing-page A/B test.
Run from project root: python -m src.gen_p3_data
"""
import numpy as np
import pandas as pd
from pathlib import Path

rng = np.random.default_rng(42)
days = pd.date_range("2026-07-01", "2026-09-30")          # 92 days

# channel: (mean daily spend, avg ROAS, elasticity b, CPL, CAC, avg order value, repeat orders 12m)
CH = {
    "Meta Retargeting": (11200, 6.1, 0.48, 116,  483, 2946, 1.08),
    "Google Search":    (33800, 4.1, 0.75, 184,  687, 2817, 0.90),
    "Meta Prospecting": (29300, 3.2, 0.78, 136,  819, 2621, 0.60),
    "Influencer":       (17700, 2.6, 0.95, 202, 1026, 2668, 0.70),
    "YouTube":          (15000, 1.9, 0.90, 175, 1285, 2441, 0.52),
    "Google Display":   (12800, 1.8, 0.72, 153, 1361, 2450, 0.36),
}

rows = []
for ch, (sp, roas, b, cpl, cac, aov, _) in CH.items():
    spend = rng.lognormal(np.log(sp) - 0.08, 0.40, len(days))
    a = roas * sp / sp ** b                                 # revenue = a * spend^b
    revenue = a * spend ** b * rng.lognormal(0, 0.12, len(days))
    customers = rng.poisson(revenue / aov)
    leads = rng.poisson(customers * cac / cpl)
    clicks = rng.poisson(leads / 0.10)
    impressions = rng.poisson(clicks / 0.02)
    for i, d in enumerate(days):
        rows.append((d.date(), ch, int(spend[i]), int(impressions[i]), int(clicks[i]),
                     int(leads[i]), int(customers[i]), int(revenue[i])))

camp = pd.DataFrame(rows, columns=["date", "channel", "spend_inr", "impressions",
                                   "clicks", "leads", "customers", "revenue_inr"])
assump = pd.DataFrame([(c, v[5], v[6], 0.45) for c, v in CH.items()],
                      columns=["channel", "avg_order_value_inr", "repeat_orders_12m", "gross_margin"])

# landing-page A/B test: 21 days, control about 3.15% vs new page about 3.75%
ab = []
for d in pd.date_range("2026-09-01", periods=21):
    for v, p in (("A_control", 0.0315), ("B_new_page", 0.0375)):
        n = int(rng.normal(1420, 90))
        ab.append((d.date(), v, n, int(rng.binomial(n, p))))
ab = pd.DataFrame(ab, columns=["date", "variant", "visitors", "conversions"])

out = Path("data/raw"); out.mkdir(parents=True, exist_ok=True)
camp.to_csv(out / "p3_campaign_daily.csv", index=False)
assump.to_csv(out / "p3_channel_assumptions.csv", index=False)
ab.to_csv(out / "p3_ab_test.csv", index=False)

g = camp.groupby("channel").sum(numeric_only=True)
print("campaign rows:", camp.shape, "| ab rows:", ab.shape)
print("total spend (Cr):", round(g.spend_inr.sum() / 1e7, 2), "| blended ROAS:", round(g.revenue_inr.sum() / g.spend_inr.sum(), 2))
print((g.revenue_inr / g.spend_inr).round(2).to_string())