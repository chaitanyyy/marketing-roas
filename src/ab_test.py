import math
import pandas as pd
from scipy.stats import norm


def load():
    from src.config import get_engine
    return pd.read_sql("SELECT variant, SUM(visitors) AS v, SUM(conversions) AS c "
                       "FROM ab_test GROUP BY variant", get_engine()).set_index("variant")


def analyse(d, alpha=0.05, power=0.80, min_lift=0.005):
    nA, cA = float(d.loc["A_control", "v"]), float(d.loc["A_control", "c"])
    nB, cB = float(d.loc["B_new_page", "v"]), float(d.loc["B_new_page", "c"])
    pA, pB = cA / nA, cB / nB
    pool = (cA + cB) / (nA + nB)
    z = (pB - pA) / math.sqrt(pool * (1 - pool) * (1 / nA + 1 / nB))
    p = 2 * (1 - norm.cdf(abs(z)))
    se = math.sqrt(pA * (1 - pA) / nA + pB * (1 - pB) / nB)
    lo, hi = (pB - pA) - norm.ppf(1 - alpha / 2) * se, (pB - pA) + norm.ppf(1 - alpha / 2) * se
    za, zb = norm.ppf(1 - alpha / 2), norm.ppf(power)
    need = math.ceil((za + zb) ** 2 * (pA * (1 - pA) + (pA + min_lift) * (1 - pA - min_lift)) / min_lift ** 2)
    print(f"A control : {int(nA):,} visitors, {int(cA):,} conversions, {pA:.2%}")
    print(f"B new page: {int(nB):,} visitors, {int(cB):,} conversions, {pB:.2%}")
    print(f"Relative lift {pB / pA - 1:+.0%} | z = {z:.2f} | p = {p:.5f}")
    print(f"95% CI for difference: {lo * 100:+.2f} to {hi * 100:+.2f} percentage points")
    print(f"Visitors per variant needed to detect {min_lift * 100:.1f} pt lift (80% power): {need:,} (had {int(min(nA, nB)):,})")


if __name__ == "__main__":
    analyse(load())