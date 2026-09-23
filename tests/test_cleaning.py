"""Three quick checks on the cleaning rules.

A test = tiny made-up data where the right answer is known + an assert.
If a rule is ever changed by accident, one of these fails loudly.

Run with:  python -m pytest -q
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.append(str(Path(__file__).resolve().parents[1]))

from src import cleaning


def toy_data():
    """Four listings: a good one, an absurd price, a 92-night long-stay,
    and a dead one (no reviews, nothing bookable)."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "neighbourhood_group": ["Mitte", "Pankow", "Spandau", "Neukölln"],
        "room_type": ["Entire home/apt", "Private room",
                      "Entire home/apt", "Private room"],
        "price": [120.0, 5000.0, 90.0, 55.0],
        "minimum_nights": [2, 3, 92, 1],
        "number_of_reviews": [40, 12, 3, 0],
        "calculated_host_listings_count": [1, 8, 1, 1],
        "availability_365": [200, 150, 300, 0],
        "license": ["03/Z/RA/12345-20",
                    "Legal entity name and Legal form: Example GmbH",
                    None,
                    "First name and Last name: Test Person"],
    })


def test_cleaning_keeps_only_the_good_listing():
    out = cleaning.clean_listings(toy_data())
    assert list(out["id"]) == [1]


def test_licence_type_gives_safe_categories():
    cats = toy_data()["license"].apply(cleaning.licence_type)
    assert cats.tolist() == ["registration", "company", "missing", "person"]


def test_professional_flag():
    out = cleaning.add_columns(toy_data())
    assert out.loc[out["id"] == 2, "is_professional"].item() == True
    assert out.loc[out["id"] == 1, "is_professional"].item() == False
