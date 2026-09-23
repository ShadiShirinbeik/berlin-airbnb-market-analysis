"""Cleaning rules for the Inside Airbnb Berlin summary file.

Each rule is a small function, so the notebook can report how many rows each
one removed and tests/test_cleaning.py can check the logic on a tiny
hand-made frame.

Column meanings follow the official Inside Airbnb data dictionary:
https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import config as cfg

EXPECTED_COLUMNS = [
    "id", "name", "host_id", "host_profile_id", "host_name",
    "neighbourhood_group", "neighbourhood", "latitude", "longitude",
    "room_type", "price", "minimum_nights", "number_of_reviews",
    "last_review", "reviews_per_month", "calculated_host_listings_count",
    "availability_365", "number_of_reviews_ltm", "license",
]


def load_listings(path=None) -> pd.DataFrame:
    """Read the raw CSV and check the columns are the ones we expect.

    Inside Airbnb has changed this file's schema before. Failing loudly here
    beats a notebook halfway down producing wrong numbers.
    """
    path = path or cfg.LISTINGS_FILE
    if not path.exists():
        raise FileNotFoundError(
            f"Expected {path}.\n"
            "Download listings.csv for Berlin from "
            "https://insideairbnb.com/get-the-data/ — see data/README.md."
        )

    df = pd.read_csv(path)
    missing = [c for c in EXPECTED_COLUMNS if c not in df.columns]
    if missing:
        print(f"  warning: expected columns not found: {missing}")
        print(f"  columns present: {list(df.columns)}")
    return df


def parse_price(df: pd.DataFrame) -> pd.DataFrame:
    """Make sure price is numeric.

    In the June 2026 snapshot the column already arrives numeric (in euros —
    the Inside Airbnb dictionary notes any currency symbol is an export
    artefact). Older snapshots shipped it as text like "$85.00", so the
    parser handles both and is safe to run twice.
    """
    out = df.copy()
    if not pd.api.types.is_numeric_dtype(out["price"]):
        cleaned = (
            out["price"].astype(str)
            .str.replace(r"[$,]", "", regex=True)
            .str.strip()
        )
        out["price"] = pd.to_numeric(cleaned, errors="coerce")
    return out


def classify_licence(s: pd.Series) -> pd.Series:
    """Sort the free-text licence column into safe categories.

    PRIVACY: since EU Regulation 2024/1028 became applicable (20 May 2026),
    this column can contain real host names and street addresses. This
    function is the ONLY place it is touched; everything downstream works
    with the category, never the raw text.

    Categories: registration_number, company_disclosure,
    individual_disclosure, other (non-empty but unmatched), missing.
    """
    out = pd.Series("other", index=s.index, dtype="object")
    text = s.fillna("").astype(str)
    for name, pattern in cfg.LICENCE_PATTERNS.items():
        hit = text.str.contains(pattern, case=False, regex=True) & out.eq("other")
        out[hit] = name
    out[s.isna() | text.str.strip().eq("")] = "missing"
    return out


def drop_invalid_price(df: pd.DataFrame, max_price: int | None = None) -> pd.DataFrame:
    """Remove listings with no price, a zero price, or an implausible one.

    Missing price is not random here: almost every listing with
    availability_365 = 0 shows no price (nothing bookable, nothing to
    quote). Notebook 01 demonstrates that before this rule is applied.
    """
    max_price = max_price or cfg.MAX_PRICE
    mask = df["price"].notna() & df["price"].gt(0) & df["price"].le(max_price)
    return df.loc[mask].copy()


def drop_long_stay_listings(df: pd.DataFrame, max_nights: int | None = None) -> pd.DataFrame:
    """Remove listings above the short-term threshold (default 90 nights).

    These are not expensive short stays — they are a different market
    ("Wohnen auf Zeit", outside Berlin's short-term letting rules), and
    about a third of the file. They are analysed as a finding in notebook 01
    and then excluded from the short-term price analysis.
    """
    max_nights = max_nights or cfg.SHORT_TERM_MAX_NIGHTS
    return df.loc[df["minimum_nights"].le(max_nights)].copy()


def drop_inactive_listings(df: pd.DataFrame) -> pd.DataFrame:
    """Remove listings with no reviews AND no availability.

    Nobody has stayed and nobody can book: the asking price is aspirational.
    Note the AND — a listing with no reviews but open availability is simply
    new, and is kept.
    """
    mask = df["number_of_reviews"].gt(0) | df["availability_365"].gt(0)
    return df.loc[mask].copy()


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add the derived columns used across the notebooks."""
    out = df.copy()

    # log price, guarded so a stray non-positive value gives NaN, not -inf
    out["log_price"] = np.where(
        out["price"] > 0, np.log(out["price"].where(out["price"] > 0)), np.nan
    )

    out["is_entire_home"] = out["room_type"].eq("Entire home/apt")
    out["is_short_term"] = out["minimum_nights"].le(cfg.SHORT_TERM_MAX_NIGHTS)

    out["host_listings"] = out["calculated_host_listings_count"]
    out["is_professional_host"] = out["host_listings"].ge(cfg.PROFESSIONAL_HOST_THRESHOLD)
    out["host_type"] = np.select(
        [out["host_listings"].eq(1),
         out["host_listings"].lt(cfg.PROFESSIONAL_HOST_THRESHOLD)],
        ["Single listing", "Small multi-host"],
        default="Professional operator",
    )
    out.loc[out["host_listings"].isna(), "host_type"] = np.nan

    out["licence_category"] = classify_licence(out["license"])
    out["has_licence"] = out["licence_category"].ne("missing")
    out["is_company_run"] = out["licence_category"].eq("company_disclosure")

    out["reviews_per_month"] = out["reviews_per_month"].fillna(0)
    out["is_central"] = out["neighbourhood_group"].isin(cfg.CENTRAL_DISTRICTS)
    return out


def check_districts(df: pd.DataFrame) -> None:
    """Warn if the district names in config stop matching the data."""
    present = set(df["neighbourhood_group"].dropna().unique())
    configured = set(cfg.ALL_DISTRICTS)
    if configured - present:
        print(f"  warning: in config but not in data: {sorted(configured - present)}")
    if present - configured:
        print(f"  warning: in data but not in config: {sorted(present - configured)}")
        print("  -> update ALL_DISTRICTS / CENTRAL_DISTRICTS in src/config.py")


def clean_listings(raw: pd.DataFrame, verbose: bool = True) -> pd.DataFrame:
    """Full pipeline: features on everything, then filter to the priced
    short-term market.

    Prints a row-loss audit. Anyone can drop rows; showing which rows and
    why is what makes the result checkable.
    """
    steps = [("raw rows", len(raw))]

    df = add_features(parse_price(raw))

    df = drop_invalid_price(df)
    steps.append(("after removing unpriced / implausible prices", len(df)))

    df = drop_long_stay_listings(df)
    steps.append((f"after removing >{cfg.SHORT_TERM_MAX_NIGHTS}-night listings", len(df)))

    df = drop_inactive_listings(df)
    steps.append(("after removing inactive listings", len(df)))

    if verbose:
        audit = pd.DataFrame(steps, columns=["step", "rows"])
        audit["removed"] = -audit["rows"].diff().fillna(0).astype(int)
        audit["pct_of_raw"] = (audit["rows"] / steps[0][1] * 100).round(1)
        print(audit.to_string(index=False))
        print()
        check_districts(df)

    return df.reset_index(drop=True)


def winsorize(s: pd.Series, lower: float = 0.0, upper: float = 0.99) -> pd.Series:
    """Clip a series at the given quantiles — for CHARTS ONLY.

    Every statistical test in this project runs on the untouched data.
    """
    return s.clip(s.quantile(lower), s.quantile(upper))
