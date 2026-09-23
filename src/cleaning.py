"""Loading, cleaning and the derived columns.

Four small functions. Each cleaning decision prints what it removed, so
the notebook shows a clear before/after story.
"""
import numpy as np
import pandas as pd

from . import config as cfg


def load_listings():
    """Read the raw file (and fail with a helpful message if it is missing)."""
    if not cfg.LISTINGS_FILE.exists():
        raise FileNotFoundError(
            "data/raw/listings.csv not found. Download the Berlin summary "
            "file from https://insideairbnb.com/get-the-data/ (see data/README.md)."
        )
    return pd.read_csv(cfg.LISTINGS_FILE)


def licence_type(value):
    """Turn one raw licence entry into a safe category.

    PRIVACY: since 20 May 2026 (EU rules) this column can contain real
    host names and home addresses. This function is the only place the
    raw text is read - everywhere else uses the category it returns.
    """
    if pd.isna(value) or str(value).strip() == "":
        return "missing"
    text = str(value).lower()
    if "legal entity" in text:
        return "company"          # e.g. "Legal entity name ... GmbH ..."
    if "first name" in text:
        return "person"           # e.g. "First name and Last name: ..."
    if len(text) > 3 and text[:2].isdigit() and text[2] == "/":
        return "registration"     # e.g. "03/Z/RA/003410-18"
    return "other"


def add_columns(df):
    """Add the handful of derived columns the notebooks use."""
    out = df.copy()
    out["is_entire_home"] = out["room_type"] == "Entire home/apt"
    out["is_short_term"] = out["minimum_nights"] <= cfg.MAX_NIGHTS
    out["is_central"] = out["neighbourhood_group"].isin(cfg.CENTRAL_DISTRICTS)
    out["is_professional"] = (
        out["calculated_host_listings_count"] >= cfg.PROFESSIONAL_MIN
    )
    out["licence_type"] = out["license"].apply(licence_type)
    out["has_licence"] = out["licence_type"] != "missing"
    return out


def clean_listings(df):
    """Filter to the priced short-term market, printing each step."""
    df = add_columns(df)
    print(f"start:                              {len(df):>6,} listings")

    df = df[df["price"].notna() & (df["price"] > 0) & (df["price"] <= cfg.MAX_PRICE)]
    print(f"with a usable price (<= {cfg.MAX_PRICE} EUR):   {len(df):>6,}")

    df = df[df["minimum_nights"] <= cfg.MAX_NIGHTS]
    print(f"short-term only (<= {cfg.MAX_NIGHTS} nights):    {len(df):>6,}")

    df = df[(df["number_of_reviews"] > 0) | (df["availability_365"] > 0)]
    print(f"active (has reviews or open dates): {len(df):>6,}")

    return df.reset_index(drop=True)
