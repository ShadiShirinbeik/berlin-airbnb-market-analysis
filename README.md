# Berlin's Short-Term Rental Market: What Sets the Price, and Who Runs It?

What sets the nightly price in Berlin — and how much of the market sits just
outside the rules. **12,855 Airbnb listings** from the Inside Airbnb snapshot
of 26 June 2026, analysed end to end in Python.

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Business Questions Addressed

One practical question — **is Berlin's short-term rental market worth
entering, and what would you charge?** — split into six.

| # | Question | Why it takes work | Method | Notebook |
|---|---|---|---|---|
| 1 | Which listings are real? | A third have no price — and that turns out to be systematic, not random | Documented cleaning rules | `01` |
| 2 | Who supplies this market? | One host runs 261 listings; EU disclosure rules now reveal which listings are company-operated | Concentration measures, licence classification | `01` |
| 3 | Does regulation show up in the data? | The single most common minimum stay is 92 nights — just above Berlin's 90-day short-term threshold | Descriptive analysis, z-test | `01`, `03` |
| 4 | How sure are we about the prices? | An average from one snapshot is an estimate; price is skewed, so the usual formula strains | Confidence intervals, formula vs bootstrap | `02` |
| 5 | Is the central premium about location? | Central listings are also more often entire flats — and those cost more anywhere | OLS regression on log(price), train/test split | `04` |
| 6 | Are there natural types of listing? | k-means returns however many groups you ask for, whether or not they exist | k-means, checked against DBSCAN | `05` |

Each notebook answers the question the one before it raised: `02` shows Mitte
looks expensive, `03` tests whether that is real, `04` asks how much survives
once room type is held fixed.

---

## Key Insights & Findings

**1. Supply is concentrated: 3.8% of hosts control 27% of all listings.**
310 hosts run 5 or more listings each; the largest runs 261. Under the EU
short-term rental regulation in force since 20 May 2026, 20% of all listings
now carry a company disclosure — this is a business landscape, not
home-sharing.

**2. A third of the market sits just outside the short-term rules.**
The single most common minimum stay is **92 nights** (29% of all listings —
more than those set to one night). Berlin's Zweckentfremdungsverbot covers
day- and week-based tourist lets but not furnished lets of three months or
more, and 92 nights clears that threshold. The pattern is consistent with
hosts positioning outside the short-term regime; the data cannot prove
intent.

**3. Licence display splits the market almost perfectly: 98% vs 7%.**
Among short-term listings, 98% display a registration number — Airbnb has
blocked unregistered short-term listings in Berlin since March 2023. Among
92-night-plus listings, only 7% do, because the requirement does not apply to
them. Berlin's registration mandate is visibly enforced exactly where it
applies, and nowhere else.

**4. The typical short-term listing charges €153 a night; entire homes
command a 93% premium.**
Across the cleaned short-term market (6,995 priced listings), the median is
€153 and the mean €182 (95% CI: €179–185). An entire home runs €95/night
above a private room (Cohen's d = 0.88 — a large effect by any convention).

**5. Central location adds 13.5% — less than it first appears.**
The raw centre-vs-outer gap is +17%, but central districts also hold more
entire flats. After controlling for room type in an OLS model
(test R² = 0.43), the location premium itself is +13.5%; Mitte tops the
controlled ranking at +10% vs the reference district, Reinickendorf sits at
−28%.

**Bottom line:** Berlin's Airbnb market is professionalised, visibly shaped
by regulation, and priced primarily by what you let (room type) before where
you let it (district).

---

## Tech Stack

| Category | Tools |
|---|---|
| **Data handling** | pandas, NumPy |
| **Statistics** | SciPy (t-test, z-test, bootstrap CI), statsmodels |
| **Machine learning** | scikit-learn — LinearRegression, KMeans, DBSCAN, StandardScaler |
| **Visualisation** | matplotlib, seaborn |
| **Environment** | Python 3.11, Jupyter Lab, Git |

---

## Data

One file, downloaded by hand — no API, no account.

| | |
|---|---|
| **Source** | [Inside Airbnb](https://insideairbnb.com/get-the-data/) — Berlin |
| **File** | `listings.csv` (the 19-column summary, **not** `listings.csv.gz`) |
| **Snapshot** | 26 June 2026 · 12,855 listings |
| **Licence** | [CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) |

Column dictionary, data quality issues and the privacy note on the `license`
column: **[`data/README.md`](data/README.md)**.

Inside Airbnb publishes a new scrape every quarter, so the snapshot date is
recorded here and in `src/config.py` — without it these numbers cannot be
reproduced.

---

## Project Structure

```
├── notebooks/          the analysis, in reading order (01 → 05)
│   ├── 01_cleaning_eda.ipynb          cleaning audit, market structure, the 92-night finding
│   ├── 02_confidence_intervals.ipynb  price distribution, formula vs bootstrap CIs
│   ├── 03_hypothesis_testing.ipynb    district and host-type comparisons
│   ├── 04_price_regression.ipynb      OLS on log(price), the controlled location premium
│   └── 05_segmentation.ipynb          k-means host archetypes, DBSCAN check
├── src/                importable logic
│   ├── config.py       paths, thresholds, district names — every judgement call in one place
│   ├── cleaning.py     one function per cleaning rule
│   ├── stats_utils.py  confidence intervals, t-test, z-test
│   └── viz.py          shared plot theme
├── tests/              a few quick sanity checks on the cleaning rules
├── data/               gitignored — see data/README.md to download
└── reports/figures/    charts written by the notebooks
```

Analysis logic lives in `src/`, not in notebook cells — so there is exactly
one definition of each cleaning rule, and each notebook cell stays a question
and a result rather than forty lines of reshaping.

---

## Running It

```bash
git clone https://github.com/<your-username>/berlin-airbnb-market-analysis.git
cd berlin-airbnb-market-analysis

python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Download listings.csv for Berlin from https://insideairbnb.com/get-the-data/
# and save it to data/raw/listings.csv

jupyter lab notebooks/
```

Run the notebooks in order — `01` writes the cleaned file the rest read.

---

## Method Notes

- **Confidence intervals computed two ways.** The t formula assumes the
  sampling distribution of the mean is roughly normal; price is heavily
  right-skewed. Notebook 02 computes every interval by formula *and* by
  bootstrap and compares them — where they diverge, the bootstrap is the one
  without the assumption.
- **Every test reports an interval and an effect size, not just a p-value.**
  With thousands of listings almost any difference is statistically
  significant, so Cohen's d says whether it is also large enough to matter.
- **z-test for rates, t-test for amounts.** Licence display and
  professional-host share are proportions; price is a continuous amount.
- **log(price) as the regression target.** Price spans orders of magnitude;
  fitted raw, a handful of expensive listings dominate the model.
- **DBSCAN as a check on k-means.** k-means returns k groups whether or not
  they exist; DBSCAN picks the number itself and labels isolated points as
  noise, showing how much of the segmentation is real structure.
- **Judgement calls live in `config.py`** — the price cap, the 90-night
  threshold, what counts as "central" — where they can be argued with.

---

## Limitations

- **A missing licence value is not proof of an unregistered listing.** The EU
  disclosure regulation had been in force for five weeks at this snapshot,
  and Berlin had [paused issuing new registration numbers](https://www.berlin.de/sen/wohnen/rechtliches/zweckentfremdungsverbot/)
  while implementing it.
- **The 92-night pattern is consistent with regulatory positioning, not
  proof of it.** The data shows the spike; it cannot show intent.
- **Prices are asking prices in peak season.** June listings at the price
  the host set — not what guests paid, and not what a January scrape would
  show.
- **The file has no flat size, amenities or review scores** — all obvious
  price drivers, which caps what any model here can explain (test R² = 0.43).
- **Nothing here is causal.** Listings were not randomly assigned to
  districts or host types.
- **The `license` column contains personal data** (host names and addresses
  under the EU disclosure rules). Its raw contents are never printed or
  plotted; only derived categories are used.

---

## Licence

Code: MIT. Data © Inside Airbnb under
[CC BY 4.0](http://creativecommons.org/licenses/by/4.0/) — see
[`data/README.md`](data/README.md).
