import numpy as np
import pandas as pd

from src.config import get_engine
from src.channel_model import fit_curves

engine = get_engine()
camp = pd.read_sql("SELECT * FROM campaign_daily", engine)


def test_row_counts():                       # 92 days x 6 channels
    assert len(camp) == 92 * 6
    assert camp.groupby("channel").size().eq(92).all()


def test_funnel_shrinks_at_every_stage():
    g = camp.groupby("channel")[["impressions", "clicks", "leads", "customers"]].sum()
    assert (g.impressions > g.clicks).all()
    assert (g.clicks > g.leads).all()
    assert (g.leads > g.customers).all()


def test_sql_scorecard_matches_pandas():
    v = pd.read_sql("SELECT channel, roas, cac, cpl FROM channel_metrics", engine).set_index("channel").astype(float)
    g = camp.groupby("channel").sum(numeric_only=True)
    assert np.allclose(v.roas, (g.revenue_inr / g.spend_inr).reindex(v.index), atol=0.011)
    assert np.allclose(v.cac, (g.spend_inr / g.customers).reindex(v.index), atol=1)
    assert np.allclose(v.cpl, (g.spend_inr / g.leads).reindex(v.index), atol=1)


def test_curves_show_diminishing_returns():
    c = fit_curves(camp)
    assert ((c.b > 0) & (c.b < 1.2)).all()
    assert c.loc["Meta Retargeting", "b"] < c.loc["Influencer", "b"]   # saturates faster
    assert (c.marginal_roas < c.avg_roas * 1.05).all()                 # next rupee never beats the average by much


def test_budget_allocator_spends_exactly_the_extra():
    from src.budget import base, greedy
    extra = 100_000
    added = sum(greedy(extra)[ch] - base[ch] for ch in base)
    assert abs(added - extra) < 1


def test_ab_test_data_is_valid():
    ab = pd.read_sql("SELECT * FROM ab_test", engine)
    assert len(ab) == 42
    assert (ab.conversions <= ab.visitors).all()