# Data

One file. No API, no account, no download script — fetched by hand.

---

## Where to get it

1. Go to **https://insideairbnb.com/get-the-data/**
2. Scroll to the **Berlin, Berlin, Germany** section
3. Download **`listings.csv`** — the row described as
   *"Summary information and metrics for listings in Berlin"*
4. Save it as **`data/raw/listings.csv`**

> **Take the file named `listings.csv`, not `listings.csv.gz`.**
> Both are called "listings". The `.gz` one is the detailed export with
> around 80 columns; the plain `.csv` is the 19-column summary this project
> is built on.

The file is about 3.5 MB.

---

## Snapshot used

| | |
|---|---|
| **City** | Berlin, Germany |
| **Snapshot date** | 26 June 2026 |
| **Rows** | 12,855 listings |
| **Columns** | 19 |
| **Licence** | [Creative Commons Attribution 4.0](http://creativecommons.org/licenses/by/4.0/) |
| **Publisher** | Inside Airbnb |

The snapshot date is the scrape date: prices, minimum stays and licence
fields describe that day, `availability_365` looks 365 days forward from it,
and review counts cover each listing's whole life. Inside Airbnb publishes a
new scrape roughly every quarter and archives old ones, so this date (also in
`src/config.py`) is what makes the numbers reproducible. Their
[data assumptions page](https://insideairbnb.com/data-assumptions/) explains
how the fields are derived and is worth reading before drawing strong
conclusions.

---

## Columns

Definitions follow the
[official Inside Airbnb data dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit).

| Column | Type | Meaning |
|---|---|---|
| `id` | int | Airbnb's identifier for the listing |
| `name` | text | Listing title |
| `host_id` | int | Airbnb's identifier for the host (79 missing) |
| `host_profile_id` | int | Identifier for the host's profile |
| `host_name` | text | Host's first name |
| `neighbourhood_group` | text | Berlin district (Bezirk) — 12 values |
| `neighbourhood` | text | Sub-district (Ortsteil) — 138 values |
| `latitude`, `longitude` | float | WGS84, deliberately fuzzed by Airbnb (~150 m) |
| `room_type` | text | Entire home/apt · Private room · Shared room · Hotel room |
| `price` | float | Nightly price in **euros** — 33.8% missing, see below |
| `minimum_nights` | int | Minimum stay — see the 92-night note below |
| `number_of_reviews` | int | Reviews all time |
| `last_review` | date | Date of the most recent review |
| `reviews_per_month` | float | Missing means zero reviews, not missing data |
| `calculated_host_listings_count` | int | Listings this host runs **in Berlin** |
| `availability_365` | int | Nights bookable in the next 365 days |
| `number_of_reviews_ltm` | int | Reviews in the last 12 months |
| `license` | text | Free text — see the privacy warning below |

---

## ⚠️ Privacy: the `license` column contains personal data

Since [EU Regulation 2024/1028](https://hnts.legal/post/zweckentfremdungsverbot-und-eu-meldepflicht---was-sich-in-berlin-ab-mai-2026-andert)
on short-term rental data became applicable on **20 May 2026**, this column
mixes three kinds of content:

| Content | Share | Example shape |
|---|---|---|
| Berlin registration number | 35% | `07/Z/AZ/009030-20` |
| Company disclosure | 20% | `Legal entity name and Legal form: … GmbH … HRB …` |
| **Individual disclosure — real names and street addresses** | 13% | `First name and Last name: … Contact address: …` |
| Missing | 32% | |

**Never print, plot or commit the raw contents of this column.** The project
classifies it into the categories above (`src/config.py` →
`LICENCE_PATTERNS`) and works only with the category. This also means the
column is analytically richer than a yes/no flag: it says which listings are
run by registered companies.

---

## Known issues, and how the project handles them

| Issue | What is behind it | Rule |
|---|---|---|
| `price` missing on 33.8% of rows | **Systematic, not random**: 99.9% of listings with `availability_365 = 0` show no price (nothing bookable → no price to show); most of the rest have 90+ night minimums | Unpriced rows excluded; the mechanism is reported in notebook 01 |
| Extreme prices | p99 ≈ €632, max over €10,000 — errors or whole villas | Dropped above `MAX_PRICE = 1000` (~26 listings) |
| `minimum_nights` spike at **92** | 29% of all listings — just above Berlin's 90-day short-term threshold ([Zweckentfremdungsverbot](https://www.berlin.de/sen/wohnen/rechtliches/zweckentfremdungsverbot/)); lets of 3+ months fall outside the short-term regime | Treated as a separate market: reported as a headline finding, then excluded from the short-term price analysis (`SHORT_TERM_MAX_NIGHTS = 90`) |
| No reviews **and** no availability | Dormant listings; their price is aspirational | Dropped (a new listing with open availability is kept) |
| `license` missing | Not proof of non-registration: the EU rule was 5 weeks old at this snapshot and Berlin had [paused issuing new numbers](https://www.berlin.de/sen/wohnen/rechtliches/zweckentfremdungsverbot/) | Flagged, never asserted as non-compliance |
| `reviews_per_month` missing | Means zero reviews | Filled with 0 |
| Fuzzed coordinates | Airbnb shifts locations ~150 m for privacy | Fine for district analysis, not street-level claims |

### What the file does not contain

No flat size, bedroom count, amenities, photos, review scores or host
response data. All are obvious price drivers; their absence caps what any
model on this file can explain. They exist in the detailed `listings.csv.gz`
export, at the cost of a much larger and messier file.

---

## Attribution

> Data from Inside Airbnb (insideairbnb.com), Berlin snapshot of
> 26 June 2026, licensed under CC BY 4.0.
