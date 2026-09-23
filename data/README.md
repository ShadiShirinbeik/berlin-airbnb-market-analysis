# Data

One file, downloaded by hand.

## How to get it

1. Open **https://insideairbnb.com/get-the-data/**
2. Scroll to **Berlin, Berlin, Germany**
3. Download **`listings.csv`** — the row described as *"Summary information
   and metrics for listings in Berlin"*
4. Save it as **`data/raw/listings.csv`**

> Take `listings.csv`, **not** `listings.csv.gz` — both are called
> "listings", but the `.gz` one is a different, much larger file.

## Snapshot used

| | |
|---|---|
| Snapshot date | 26 June 2026 (the day Inside Airbnb scraped Airbnb) |
| Rows | 12,855 listings |
| Columns | 19 |
| Licence | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |

Inside Airbnb publishes a new snapshot every quarter, so numbers from a
different date will differ.

## The main columns

| Column | Meaning |
|---|---|
| `price` | Nightly price in **euros** — missing on a third of rows (systematic: listings with zero availability show no price) |
| `minimum_nights` | Minimum stay — the most common value is 92 (see notebook 01) |
| `room_type` | Entire home/apt · Private room · Shared room · Hotel room |
| `neighbourhood_group` | Berlin district (12 values, some abbreviated by Inside Airbnb) |
| `calculated_host_listings_count` | How many Berlin listings this host runs |
| `availability_365` | Nights bookable in the next 365 days |
| `number_of_reviews`, `reviews_per_month` | Review counts (whole lifetime) |
| `license` | Free text — see the privacy note |

Full definitions: [official data dictionary](https://docs.google.com/spreadsheets/d/1iWCNJcSutYqpULSQHlNyGInUvHg2BoUGoNRIGa6Szc4/edit).

## ⚠️ Privacy: the `license` column

Under EU rules in force since 20 May 2026, this column can contain real
host **names and home addresses**. Never print or commit its raw contents.
The project reads it in exactly one function (`cleaning.licence_type`) and
works only with safe categories: `registration` / `company` / `person` /
`missing`.

## Attribution

> Data from Inside Airbnb (insideairbnb.com), Berlin snapshot of
> 26 June 2026, licensed under CC BY 4.0.
