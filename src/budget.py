import pandas as pd
from src.channel_model import load, fit_curves

curves = fit_curves(load())
DAYS, STEP = 30, 10_000
base = {ch: r.mean_daily_spend * DAYS for ch, r in curves.iterrows()}      # monthly spend today


def rev(ch, monthly_spend):
    r = curves.loc[ch]
    return DAYS * r.a * (monthly_spend / DAYS) ** r.b


def total(alloc):
    return sum(rev(ch, s) for ch, s in alloc.items())


def greedy(extra):
    alloc = dict(base)
    for _ in range(int(extra // STEP)):                    # each Rs 10,000 goes where it earns most
        best = max(alloc, key=lambda c: rev(c, alloc[c] + STEP) - rev(c, alloc[c]))
        alloc[best] += STEP
    return alloc


def strategies(extra):
    best_avg = curves.avg_roas.idxmax()
    return {
        "Marginal ROAS (greedy)": greedy(extra),
        f"All to best-ROAS channel ({best_avg})": {**base, best_avg: base[best_avg] + extra},
        "Split evenly": {ch: s + extra / len(base) for ch, s in base.items()},
    }


if __name__ == "__main__":
    t0 = total(base)
    out = []
    for extra in (100_000, 500_000):
        print(f"\nExtra budget Rs {extra / 1e5:.0f} lakh per month")
        for name, alloc in strategies(extra).items():
            gain = total(alloc) - t0
            print(f"  {name:48s} +Rs {gain / 1e5:5.2f} lakh revenue / month")
            out.append(dict(extra_lakh=extra / 1e5, strategy=name, gain_lakh=round(gain / 1e5, 2)))
        g = greedy(extra)
        moves = {c: round(float(g[c] - base[c]) / 1e5, 1) for c in g if g[c] > base[c]}
        print("  greedy allocation (Rs lakh):", moves)
    pd.DataFrame(out).to_csv("data/processed/budget_scenarios.csv", index=False)