"""One-line Goal and Check for each exercise, for the single Exercises slide of each deck.

The full steps live in 6141.md (sections 11-13); the slide shows only what to build and
how to know it worked. Every number below is copied from the Success Check / Self-Check
of the same exercise in 6141.md; update both together.
"""

EXERCISES = {
    "1.3": [
        ("Add an operating margin column and summarize stores by region", "`count` 12; margins from `23.6`% to `36.9`%"),
        ("Keep stores with margin `>= 30` and satisfaction `>= 4.5`", "5 stores, led by `STR-1011` (`36.89`%)"),
        ("Sort all 12 stores into Gold, Watch, and Standard tiers", "Gold `4`, Watch `5`, Standard `3`"),
    ],
    "1.4": [
        ("Total each division's budget and actual spend by quarter", "16 rows; 8 with a positive `Total_Variance`"),
        ("Find the cost centers that overspent for the whole year", "`CC-202` (`85000.0`) and `CC-404` (`28000.0`)"),
        ("Tell the finance director which VPs must explain their spending", "`0` disagreements; 6 of 16 quarters flagged"),
    ],
    "2.2": [
        ("Draw two charts side by side in one image", "the scatter climbs: correlation `0.98`"),
        ("Build a 2x2 boardroom dashboard with 4 charts", "4 charts, no overlapping titles"),
        ("Does each marketing dollar still bring in as much revenue?", "average revenue per marketing dollar: `5.08`"),
    ],
    "2.3": [
        ("Test two hypotheses and measure the revenue at risk", "correlation `-0.982`; baseline `$930,000`"),
        ("Write checks that stop bad data, then clean the file", "`clean` has `12` rows and passes all 3 checks"),
        ("Show in numbers how bad data distorts the risk report", "raw file: 4 problems; clean file: `0`"),
    ],
    "2.4": [
        ("Build the quarterly review as a reproducible pipeline", "`2024-Q4` has the highest GMV (`524.4`)"),
        ("Peer review a classmate's script with the checklist", "the hard-coded `0.125` fails question 3"),
        ("Rank regions by size, cash efficiency, and trend", "`North_America` first (margin `31.0`)"),
    ],
    "3.1": [
        ("Rank the AI portfolio and compare departments", "Fraud Operations leads (`709.6`)"),
        ("Fund projects by hours per dollar until $500,000 runs out", "4 projects, `$480,000`, `16,100` hours a year"),
        ("Test the simple method against every combination", "`1023` groups checked, `163` fit the budget"),
    ],
    "3.2": [
        ("Encode, split, fill, and scale the credit data", "every training average `0.0`, spread `1.0`"),
        ("Add one feature, then see what data leakage hides", "leaky test averages are all `0.0`"),
        ("Build one pipeline that also handles unseen categories", "6 output columns; no crash on the new applicant"),
    ],
    "3.3": [
        ("Train, predict, and evaluate a price model", "`Test RMSE: $11,539 | R-squared: 0.996`"),
        ("Show each property's error and price one new building", "MAPE `2.68`%"),
        ("Do more features give a better price model?", "model C has the lowest average RMSE (`$7,733`)"),
    ],
    "3.4": [
        ("Count the four outcomes and price the mistakes", "`TP=7, FP=1, FN=0, TN=8`; cost `$5.00`"),
        ("Test thresholds 50 to 90 and find the cheapest", "50 to 70 cost `$5`; 90 costs `$9,000`"),
        ("Price each missed fraud with its real amount", "`$0` at thresholds `72`, `73`, and `74`"),
    ],
    "4.1": [
        ("Find the nights in the run log that need attention", "alerts on `2024-12-04` and `2024-12-05`"),
        ("Keep the nightly job working without the model file", "fallback holds 3; the model holds 4"),
        ("One function for the whole night: validate, score, act, report", "`held: 4`, `needs_review: True`"),
    ],
    "4.2": [
        ("Price a campaign for customers at `0.5` or above", "net benefit `$1,899.68`; ROI `633.2`%"),
        ("Highest ROI or most money? Test thresholds 0.3 to 0.8", "best ROI at `0.8`; most money at `0.4`"),
        ("Choose the best offer for each customer", "VIP for 4, Call for 3, None for 3"),
    ],
    "4.3": [
        ("Simulate a wider range of price changes", "gross margins from `52.5`% to `55.0`%"),
        ("Find the price cut each at-risk product needs", "`PRD-200` needs the deepest cut (`-11.4`%)"),
        ("Find each product's best price for the season", "5 cuts, 4 rises, 3 unchanged"),
    ],
    "4.4": [
        ("Audit approval rates at the current threshold", "ratio `0.286`: below the four-fifths rule"),
        ("Turn the audit into a function and save a board record", "`Status`: `Board review required`"),
        ("Can one shared threshold fix the gap?", "only `0.45` and `0.50` reach `0.8` or more"),
    ],
}
