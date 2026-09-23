"""Four quick sanity checks on the cleaning rules.

The idea of a test: build tiny data where the correct answer is known in
advance, run the function, and assert the answer came back. If someone later
changes a rule by accident, one of these fails loudly instead of a headline
number changing silently.

Run with:  pytest -q
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import cleaning  # noqa: E402


def make_toy() -> pd.DataFrame:
    """Four listings, each illustrating one thing the cleaner must handle:
    a normal one, an implausible price, a 92-night long-stay, and a dormant
    one (no reviews, nothing bookable)."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "host_id": [11, 12, 13, 14],
        "neighbourhood_group": ["Mitte", "Pankow", "Spandau", "Neukölln"],
        "room_type": ["Entire home/apt", "Private room", "Entire home/apt", "Private room"],
        "price": [120.0, 5000.0, 90.0, 55.0],
        "minimum_nights": [2, 3, 92, 1],
        "number_of_reviews": [40, 12, 3, 0],
        "reviews_per_month": [1.8, 0.7, 0.1, None],
        "calculated_host_listings_count": [1, 8, 1, 1],
        "availability_365": [200, 150, 300, 0],
        "license": ["03/Z/RA/12345-20",
                    "Legal entity name and Legal form: Example GmbH",
                    None,
                    "First name and Last name: Test Person"],
    })


def test_pipeline_keeps_only_the_real_short_term_listing():
    # Of the four toy listings, only #1 is a priced, short-term, active
    # listing. #2 has an implausible price, #3 is a 92-night long-stay,
    # #4 is dormant (no reviews AND no availability).
    out = cleaning.clean_listings(make_toy(), verbose=False)
    assert list(out["id"]) == [1]


def test_price_cap_removes_the_implausible_listing():
    out = cleaning.drop_invalid_price(make_toy(), max_price=1000)
    assert 2 not in out["id"].values
    assert (out["price"] <= 1000).all()


def test_licence_text_becomes_a_safe_category():
    # The raw license column can contain personal data, so the project only
    # ever works with these categories — check each pattern lands correctly.
    cats = cleaning.classify_licence(make_toy()["license"])
    assert cats.tolist() == [
        "registration_number", "company_disclosure", "missing", "individual_disclosure",
    ]


def test_professional_host_flag_uses_the_threshold():
    out = cleaning.add_features(make_toy())
    by_id = out.set_index("id")
    assert not by_id.loc[1, "is_professional_host"]   # 1 listing
    assert by_id.loc[2, "is_professional_host"]       # 8 listings
