"""Statistical helpers.

Scope is deliberately small — three things:

1. Confidence intervals two ways: the formula (t) method and the bootstrap.
2. Two-sample t-test for comparing means.
3. Two-proportion z-test for comparing rates.

Every function returns the estimate together with an interval, never a bare
p-value. A p-value says "could this be chance?"; the interval says "how big
is it?", and only the second one is a business answer.

References
----------
Student's t interval and two-sample t-test: Moore, McCabe & Craig (2017),
    *Introduction to the Practice of Statistics*, 9th ed., ch. 7.
Percentile bootstrap: Efron & Tibshirani (1993), *An Introduction to the
    Bootstrap*, Chapman & Hall. https://doi.org/10.1201/9780429246593
Welch's t-test: Welch (1947), Biometrika 34(1-2), 28-35.
    https://doi.org/10.1093/biomet/34.1-2.28
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Callable, Sequence

import numpy as np
from scipy import stats


# ==========================================================================
# 1. Confidence intervals
# ==========================================================================
@dataclass
class Interval:
    """An estimate together with its uncertainty."""

    estimate: float
    lower: float
    upper: float
    method: str

    @property
    def width(self) -> float:
        return self.upper - self.lower

    def as_dict(self) -> dict:
        return asdict(self)

    def __str__(self) -> str:
        return (
            f"{self.estimate:,.2f}  95% CI "
            f"[{self.lower:,.2f}, {self.upper:,.2f}]  ({self.method})"
        )


def mean_ci_formula(x: Sequence[float], alpha: float = 0.05) -> Interval:
    """Confidence interval for a mean using the t distribution.

        CI = mean +/- t(alpha/2, n-1) * s / sqrt(n)

    Assumes the *sampling distribution of the mean* is roughly normal. With
    large n the central limit theorem usually delivers that even on skewed
    data — but "usually" is doing real work in that sentence, which is why
    the bootstrap version below exists for comparison.
    """
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    n = x.size
    mean = x.mean()
    se = x.std(ddof=1) / np.sqrt(n)
    crit = stats.t.ppf(1 - alpha / 2, df=n - 1)
    return Interval(mean, mean - crit * se, mean + crit * se, f"t formula, n={n:,}")


def mean_ci_bootstrap(
    x: Sequence[float], n_boot: int = 10_000, alpha: float = 0.05, seed: int = 42
) -> Interval:
    """Percentile bootstrap CI for a mean.

    Resample with replacement B times, take each resample's mean, read the
    2.5th and 97.5th percentiles. No formula, no distributional assumption —
    and on right-skewed data the interval comes out asymmetric, which is the
    honest shape the symmetric formula cannot express.
    """
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    boot = np.empty(n_boot)
    for i in range(n_boot):
        boot[i] = rng.choice(x, size=x.size, replace=True).mean()
    lo, hi = np.percentile(boot, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return Interval(float(x.mean()), float(lo), float(hi), f"bootstrap, B={n_boot:,}")


def statistic_ci_bootstrap(
    x: Sequence[float],
    stat: Callable[[np.ndarray], float] = np.median,
    n_boot: int = 10_000,
    alpha: float = 0.05,
    seed: int = 42,
) -> Interval:
    """Bootstrap CI for any statistic — e.g. the median, which has no
    textbook formula. This is the practical advantage of the method."""
    rng = np.random.default_rng(seed)
    x = np.asarray(x, dtype=float)
    x = x[~np.isnan(x)]
    vals = np.empty(n_boot)
    for i in range(n_boot):
        vals[i] = stat(rng.choice(x, size=x.size, replace=True))
    lo, hi = np.percentile(vals, [100 * alpha / 2, 100 * (1 - alpha / 2)])
    return Interval(float(stat(x)), float(lo), float(hi), f"bootstrap, B={n_boot:,}")


def proportion_ci(successes: int, n: int, alpha: float = 0.05) -> Interval:
    """Normal-approximation CI for a proportion.

        CI = p +/- z(alpha/2) * sqrt(p(1-p)/n)

    Same approximation the z-test uses, so interval and test always tell one
    story. Needs a reasonable count in both cells (rule of thumb: >= 10),
    which the function checks.
    """
    p = successes / n
    z = stats.norm.ppf(1 - alpha / 2)
    se = np.sqrt(p * (1 - p) / n)
    if min(successes, n - successes) < 10:
        print(
            f"  warning: only {min(successes, n - successes)} in the smaller "
            "cell; the normal approximation is unreliable below ~10."
        )
    return Interval(p, max(0.0, p - z * se), min(1.0, p + z * se), f"normal, n={n:,}")


# ==========================================================================
# 2. Comparing two means — t-test
# ==========================================================================
def cohens_d(a: Sequence[float], b: Sequence[float]) -> float:
    """Standardised difference between two means.

        d = (mean_a - mean_b) / pooled standard deviation

    A p-value says whether a gap is distinguishable from chance; it says
    nothing about size, and with a large sample even a trivial gap becomes
    "significant". Cohen's d puts the gap on a scale of standard deviations:
    roughly 0.2 small, 0.5 medium, 0.8 large (Cohen 1988) — rules of thumb,
    not thresholds.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    n_a, n_b = a.size, b.size
    pooled = np.sqrt(
        ((n_a - 1) * a.var(ddof=1) + (n_b - 1) * b.var(ddof=1)) / (n_a + n_b - 2)
    )
    return float((a.mean() - b.mean()) / pooled)


def t_test(
    a: Sequence[float],
    b: Sequence[float],
    label_a: str = "A",
    label_b: str = "B",
    alpha: float = 0.05,
    n_boot: int = 5_000,
    seed: int = 42,
) -> dict:
    """Two-sample t-test with a bootstrap interval on the difference.

    ``equal_var=False`` gives Welch's version, which does not assume the two
    groups share a variance — hard to defend on price data from different
    market segments, and dropping it costs almost nothing when true.

    The bootstrap interval is in the original units (euros), which is what
    makes the result actionable.
    """
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    a, b = a[~np.isnan(a)], b[~np.isnan(b)]

    t_stat, p_value = stats.ttest_ind(a, b, equal_var=False)

    rng = np.random.default_rng(seed)
    diffs = np.empty(n_boot)
    for i in range(n_boot):
        diffs[i] = (
            rng.choice(a, a.size, replace=True).mean()
            - rng.choice(b, b.size, replace=True).mean()
        )
    lo, hi = np.percentile(diffs, [100 * alpha / 2, 100 * (1 - alpha / 2)])

    return {
        "group_a": label_a,
        "group_b": label_b,
        "n_a": int(a.size),
        "n_b": int(b.size),
        "mean_a": float(a.mean()),
        "mean_b": float(b.mean()),
        "median_a": float(np.median(a)),
        "median_b": float(np.median(b)),
        "difference": float(a.mean() - b.mean()),
        "diff_ci_low": float(lo),
        "diff_ci_high": float(hi),
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "cohens_d": cohens_d(a, b),
        "significant": bool(p_value < alpha),
    }


# ==========================================================================
# 3. Comparing two proportions — z-test
# ==========================================================================
def z_test_proportions(
    successes_a: int,
    n_a: int,
    successes_b: int,
    n_b: int,
    label_a: str = "A",
    label_b: str = "B",
    alpha: float = 0.05,
) -> dict:
    """Two-proportion z-test with a CI on the difference.

    The test statistic uses the *pooled* proportion in its standard error
    (under H0 both groups share one rate); the confidence interval uses the
    *unpooled* one (there we are estimating the gap, not assuming it is
    zero). Mixing the two up is a common slip.
    """
    p_a = successes_a / n_a
    p_b = successes_b / n_b

    p_pool = (successes_a + successes_b) / (n_a + n_b)
    se_pool = np.sqrt(p_pool * (1 - p_pool) * (1 / n_a + 1 / n_b))
    z = (p_a - p_b) / se_pool
    p_value = 2 * (1 - stats.norm.cdf(abs(z)))

    se_unpool = np.sqrt(p_a * (1 - p_a) / n_a + p_b * (1 - p_b) / n_b)
    crit = stats.norm.ppf(1 - alpha / 2)
    diff = p_a - p_b

    return {
        "group_a": label_a,
        "group_b": label_b,
        "n_a": int(n_a),
        "n_b": int(n_b),
        "rate_a": p_a,
        "rate_b": p_b,
        "difference": diff,
        "diff_ci_low": diff - crit * se_unpool,
        "diff_ci_high": diff + crit * se_unpool,
        "relative_lift": diff / p_b if p_b else np.nan,
        "z_statistic": float(z),
        "p_value": float(p_value),
        "significant": bool(p_value < alpha),
    }
