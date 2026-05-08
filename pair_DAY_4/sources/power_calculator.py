"""
Sample size calculator for binary pass/fail benchmarks.

Given a baseline pass rate, target effect size, significance level, and power target,
computes the number of tasks required to detect the improvement.

Also computes the MDE (minimum detectable effect) for a fixed sample size.

Run: python power_calculator.py
"""

import math


def sample_size(p_baseline, delta, alpha=0.05, power=0.80):
    """
    Required tasks to detect `delta` percentage-point improvement at given power.
    Two-sided two-proportion z-test.
    """
    z_alpha = _z(1 - alpha / 2)   # 1.96 for alpha=0.05
    z_beta  = _z(power)            # 0.842 for power=0.80
    p2 = p_baseline + delta
    variance = p_baseline * (1 - p_baseline) + p2 * (1 - p2)
    n = (z_alpha + z_beta) ** 2 * variance / delta ** 2
    return math.ceil(n)


def mde(p_baseline, n, alpha=0.05, power=0.80):
    """
    Minimum detectable effect (percentage points) for a given sample size.
    """
    z_alpha = _z(1 - alpha / 2)
    z_beta  = _z(power)
    # Approximate: use pooled variance at baseline
    se = math.sqrt(2 * p_baseline * (1 - p_baseline) / n)
    return (z_alpha + z_beta) * se


def bootstrap_p_lower_bound(B):
    """Minimum achievable bootstrap p-value with B replicates (Efron & Hastie)."""
    return 1 / (B + 1)


def _z(p):
    """Inverse normal CDF via rational approximation (Abramowitz & Stegun 26.2.17)."""
    assert 0 < p < 1
    if p < 0.5:
        return -_z(1 - p)
    t = math.sqrt(-2 * math.log(1 - p))
    c = (2.515517, 0.802853, 0.010328)
    d = (1.432788, 0.189269, 0.001308)
    return t - (c[0] + c[1]*t + c[2]*t**2) / (1 + d[0]*t + d[1]*t**2 + d[2]*t**3)


# ── Tenacious-Bench v0.1 parameters ─────────────────────────────────────────

P_BASELINE = 0.7459   # Week 10 held-out average
N_V1       = 216      # v0.1 task count
B          = 2000     # bootstrap replicates used

if __name__ == "__main__":
    print("── Tenacious-Bench v0.1 — current benchmark ────────────────────")
    mde_v1 = mde(P_BASELINE, N_V1) * 100
    print(f"  Tasks: {N_V1}")
    print(f"  Baseline pass rate: {P_BASELINE:.1%}")
    print(f"  MDE at 80% power (α=0.05): {mde_v1:.1f} percentage points")
    print(f"  → Delta A = −2.34 pts is {2.34/mde_v1:.0%} of the MDE")
    print(f"  → p = 0.71 cannot distinguish 'no effect' from 'real gain < {mde_v1:.0f} pts'")
    print()

    print("── Sample size targets for Tenacious-Bench v0.2 ────────────────")
    for delta_pts in [3, 5, 8]:
        delta = delta_pts / 100
        n = sample_size(P_BASELINE, delta)
        print(f"  Detect +{delta_pts} pts at 80% power: {n:,} tasks")
    print()

    print("── Bootstrap p-value correction ─────────────────────────────────")
    p_min = bootstrap_p_lower_bound(B)
    print(f"  B = {B} bootstrap replicates")
    print(f"  Minimum achievable p-value: 1/(B+1) = {p_min:.4f}")
    print(f"  Correct statement: 'p < {p_min:.4f}' (not 'p = 0.0')")
    print()

    print("── Recommended v0.2 design ──────────────────────────────────────")
    n_5pt = sample_size(P_BASELINE, 0.05)
    print(f"  Minimum for +5 pt sensitivity: {n_5pt:,} tasks")
    print(f"  Recommended target (with margin): 1,200–1,500 tasks")
    print(f"  Per dimension (6 dims): 200–250 tasks each")
