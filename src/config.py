"""Paths, thresholds and constants.

Every judgement call in this project lives here rather than in a notebook
cell, so it can be found, changed and argued with in one place.

The numbers below are not defaults picked from the air — each one is
explained against what is actually in the June 2026 Berlin snapshot.
"""
from __future__ import annotations

from pathlib import Path

# --------------------------------------------------------------------------
# Paths
# --------------------------------------------------------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
FIGURES_DIR = PROJECT_ROOT / "reports" / "figures"

for _d in (RAW_DIR, FIGURES_DIR):
    _d.mkdir(parents=True, exist_ok=True)

LISTINGS_FILE = RAW_DIR / "listings.csv"          # the one input file
CLEAN_FILE = DATA_DIR / "listings_clean.csv"      # written by notebook 01

# Inside Airbnb publishes a new scrape roughly every quarter and archives the
# old ones, so the snapshot date is the only thing that makes these numbers
# reproducible.
SNAPSHOT_DATE = "2026-06-26"

# --------------------------------------------------------------------------
# Cleaning thresholds
# --------------------------------------------------------------------------
# Price is right-skewed with a very long tail: the 99th percentile is around
# 632 EUR, the 99.5th around 832, and the maximum is over 10,000. A cap at
# 1,000 removes roughly 26 listings — almost certainly data errors or whole
# villas — while leaving the real luxury segment intact.
MAX_PRICE = 1_000

# Berlin's Zweckentfremdungsverbot generally allows a secondary residence to
# be let as a holiday flat for at most 90 days a year, and the ban does not
# cover "Wohnen auf Zeit" — furnished lets of three months or more to people
# coming to Berlin to work.
#   https://www.berlin.de/sen/wohnen/rechtliches/zweckentfremdungsverbot/
#
# In this snapshot the single most common minimum_nights value is 92, on
# about 29% of all listings — more than the number set to one night. Those
# listings are positioned just outside the short-term regime, which makes
# them a different market rather than expensive short stays. They are
# reported as a headline finding in notebook 01 and then excluded from the
# price analysis.
SHORT_TERM_MAX_NIGHTS = 90

# --------------------------------------------------------------------------
# Host classification
# --------------------------------------------------------------------------
# calculated_host_listings_count is the number of listings a host runs in
# Berlin. In this snapshot 5+ covers about 27% of listings, which is a
# meaningful slice without being so rare that no comparison is possible.
PROFESSIONAL_HOST_THRESHOLD = 5

# --------------------------------------------------------------------------
# Licence column
# --------------------------------------------------------------------------
# PRIVACY WARNING
# The `license` column is free text and, since EU Regulation 2024/1028 on
# short-term rental data became applicable on 20 May 2026, many rows contain
# real host names and street addresses. Never print, plot or commit its raw
# contents. Classify it with the patterns below and work with the category
# only. The regexes are case-insensitive because both "03/Z/RA/..." and
# "03/z/ra/..." appear in the data.
LICENCE_PATTERNS = {
    # A Berlin Registriernummer, e.g. 07/Z/AZ/009030-20 or 11/3/38/710130-07
    "registration_number": r"^\s*\d{2}/[A-Za-z0-9]{1,3}/",
    # A company disclosure: "Legal entity name and Legal form: ... GmbH ..."
    "company_disclosure": r"legal entity",
    # An individual disclosure: "First name and Last name: ..."
    "individual_disclosure": r"first name",
}

# --------------------------------------------------------------------------
# Geography
# --------------------------------------------------------------------------
# Exact strings as they appear in the file. Inside Airbnb abbreviates some
# Berlin district names and spaces the hyphens inconsistently, so these are
# copied verbatim rather than typed from memory. cleaning.check_districts()
# warns if they ever stop matching.
ALL_DISTRICTS = [
    "Mitte",
    "Friedrichshain-Kreuzberg",
    "Pankow",
    "Charlottenburg-Wilm.",
    "Neukölln",
    "Tempelhof - Schöneberg",
    "Treptow - Köpenick",
    "Lichtenberg",
    "Steglitz - Zehlendorf",
    "Reinickendorf",
    "Spandau",
    "Marzahn - Hellersdorf",
]

# The four inner-city districts, which together hold about two thirds of all
# listings. This is a judgement call, which is exactly why it belongs here.
CENTRAL_DISTRICTS = [
    "Mitte",
    "Friedrichshain-Kreuzberg",
    "Pankow",
    "Neukölln",
]

# --------------------------------------------------------------------------
# Analysis
# --------------------------------------------------------------------------
RANDOM_SEED = 42
ALPHA = 0.05          # significance level used throughout
N_BOOTSTRAP = 10_000  # resamples for bootstrap confidence intervals

# --------------------------------------------------------------------------
# Plot defaults
# --------------------------------------------------------------------------
FIG_DPI = 150
FIG_SIZE = (9, 5)
PALETTE = "colorblind"   # readable with colour-vision deficiency
