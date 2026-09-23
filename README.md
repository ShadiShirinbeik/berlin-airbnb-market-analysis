# Berlin's Short-Term Rental Market: What Sets the Price, and Who Runs It?

**12,855 Airbnb listings** in Berlin (Inside Airbnb snapshot, 26 June 2026),
analysed in Python: what a listing costs, what drives that price, and how
visible Berlin's letting rules are in the data.

---

## Questions & Notebooks

| # | Question | Method | Notebook |
|---|---|---|---|
| 1 | Which listings are real, and who supplies this market? | Cleaning with documented rules, host concentration | `01_cleaning_eda` |
| 2 | How sure are we about the prices, and which gaps are real? | Confidence intervals, t-test, z-test | `02_statistics` |
| 3 | What drives the price once everything is held fixed? | Linear regression on log(price), train/test split | `03_price_regression` |

---

## Key Findings

**1. Supply is concentrated.** 3.8% of hosts run 5+ listings each and
control **27% of the market**; the largest single host runs 261 listings.

**2. A third of the market sits just outside the short-term rules.** The
single most common minimum stay is **92 nights** (29% of listings) — just
above the 90-day threshold of Berlin's short-term letting law. Consistent
with hosts positioning outside the rules; the data cannot prove intent.

**3. The registration rule is clearly visible in the data.** **97.9%** of
short-term listings display a licence (Airbnb blocks unregistered ones)
vs **7.5%** of long-stay listings, which do not need one.

**4. Room type beats location.** The median short-term listing costs
**€153/night**. An entire home costs ~**87% more** than a private room
(holding everything else fixed), while central location adds ~**14%** —
less than the raw gap of 17%, because central districts also have more
entire homes.

---

## Tech

Python · pandas · NumPy · SciPy (t-test, z-test, confidence intervals) ·
scikit-learn (linear regression) · matplotlib · seaborn · Jupyter · pytest

---

## Data

| | |
|---|---|
| Source | [Inside Airbnb](https://insideairbnb.com/get-the-data/) — Berlin, `listings.csv` (the 19-column summary) |
| Snapshot | 26 June 2026 · 12,855 listings |
| Licence | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |

Download steps, column meanings and a privacy note: [`data/README.md`](data/README.md).

---

## Project Structure

```
├── notebooks/       the analysis, in order (01 -> 03)
├── src/
│   ├── config.py    all thresholds and settings in one place
│   └── cleaning.py  loading, cleaning rules, derived columns
├── tests/           three quick checks on the cleaning rules
├── data/            gitignored - see data/README.md
└── reports/figures/ charts saved by the notebooks
```

The cleaning rules live in `src/`, not in notebook cells — one definition,
covered by tests, used everywhere.

---

## Running It

```bash
git clone https://github.com/<your-username>/berlin-airbnb-market-analysis.git
cd berlin-airbnb-market-analysis

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# download listings.csv (Berlin) from https://insideairbnb.com/get-the-data/
# and save it as data/raw/listings.csv

python -m pytest -q      # 3 tests
jupyter lab notebooks/
```

Run the notebooks in order — `01` writes the cleaned file the others read.

---

## Limitations

- **Asking prices in peak season** — what hosts ask in June, not what
  guests paid.
- **A missing licence is not proof of an unregistered listing** — long-stay
  listings don't need one, and Berlin had paused issuing new numbers while
  implementing the 2026 EU rules.
- **No flat size, amenities or review scores in the file** — the main price
  drivers are simply absent, which caps the model's R².
- **Correlations, not causes** — listings were not randomly assigned to
  districts or room types.
- **The `license` column contains personal data** (names, addresses). Its
  raw text is never printed; only safe categories are used.

---

## Licence

Code: MIT. Data © Inside Airbnb, [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/).
