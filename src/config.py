"""All the project's settings and thresholds in one place.

If a number can be argued with ("why 1000 and not 800?"), it lives here,
so there is exactly one copy to find and change.
"""
from pathlib import Path

# ---- paths -----------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
LISTINGS_FILE = PROJECT_ROOT / "data" / "raw" / "listings.csv"
CLEAN_FILE = PROJECT_ROOT / "data" / "listings_clean.csv"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"
FIGURES_DIR.mkdir(parents=True, exist_ok=True)

# The date Inside Airbnb scraped this file. They publish a new one every
# quarter, so without this date the numbers cannot be reproduced.
SNAPSHOT_DATE = "2026-06-26"

# ---- cleaning thresholds ---------------------------------------------
# 99% of priced listings are under ~632 EUR; the max is over 10,000.
# A cap at 1000 removes only ~26 listings (data errors or whole villas).
MAX_PRICE = 1000

# Berlin's short-term letting rules stop applying at lets of 3 months or
# more. Listings above 90 nights are a different market (medium-term
# furnished rentals), so the price analysis excludes them.
# https://www.berlin.de/sen/wohnen/rechtliches/zweckentfremdungsverbot/
MAX_NIGHTS = 90

# A host with this many listings or more is treated as professional.
PROFESSIONAL_MIN = 5

# ---- geography --------------------------------------------------------
# District names copied EXACTLY as they appear in the file
# (Inside Airbnb abbreviates some of them).
CENTRAL_DISTRICTS = [
    "Mitte",
    "Friedrichshain-Kreuzberg",
    "Pankow",
    "Neukölln",
]

SEED = 42
