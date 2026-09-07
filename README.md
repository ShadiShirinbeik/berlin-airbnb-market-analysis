# Berlin's Short-Term Rental Market: What Sets the Price, and Who Runs It?

Analysis of **12,856 Airbnb listings in Berlin** (Inside Airbnb snapshot,
26 June 2026) — from a raw CSV to a written recommendation, using confidence
intervals, hypothesis tests, regression and clustering.

![Tests](https://img.shields.io/badge/tests-35%20passing-brightgreen)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 🎯 Business Questions Addressed

| # | Question | Method | Notebook |
|---|---|---|---|
| 1 | What is in this file, and which listings cannot be trusted? | Data quality audit, documented cleaning rules | `01` |
| 2 | How precisely do we know prices in each district? | Confidence intervals — formula vs bootstrap | `02` |
| 3 | Which differences between districts and host types are real? | Two-sample t-test, two-proportion z-test, Cohen's d | `03` |
| 4 | What actually drives the price, once everything else is held fixed? | Linear regression with train/test split | `04` |
| 5 | Are there natural types of listing in this market? | k-means segmentation, validated with DBSCAN | `05` |

Each notebook answers the question the previous one raised. Notebook 02 shows
Mitte looks more expensive; notebook 03 tests whether that gap is bigger than
chance; notebook 04 asks how much of it survives once room type is controlled
for. Notebook 05 stops predicting and asks what structure is there at all.

Running through all of it is one question Berlin actually argues about:
**how professionalised is this market?** The `calculated_host_listings_count`
column separates someone letting a spare room from an operator running
fifteen flats, and that distinction is the subject of Berlin's
Zweckentfremdungsverbot (the law restricting the conversion of housing to
short-term letting).

---

## 📊 Key Insights & Findings


---

## 🛠️ Tech Stack

| Category | Tools |
|---|---|
| **Language** | python |
| **Data handling** | pandas, NumPy |
| **Statistics** | SciPy, statsmodels |
| **Machine learning** | scikit-learn — LinearRegression, KMeans, DBSCAN, PCA, StandardScaler |
| **Visualisation** | matplotlib, seaborn |
| **Testing & CI** | pytest, GitHub Actions |

---

## Data

| Source | File |
|---|---|
| [Inside Airbnb](https://insideairbnb.com/get-the-data/) — Berlin | `listings.csv` (the 19-column summary, 26 June 2026) |
