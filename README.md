# Yemen MarketShield AI

**An early-stage machine-learning research project for food-price analysis and experimental price-shock detection in Yemen.**

Yemen MarketShield AI explores whether monthly food, exchange-rate, and energy-price data can help describe market trends and support research into possible future wheat-price increases. The current release is a research prototype, not an operational food-security alert service.

> **Research and safety note:** The target variable `c_wheat` is the World Bank Real-Time Prices database's monthly close estimate. It must not be treated as an independently verified market observation. The current experiment does not establish that a food crisis will occur, and its predictions must not be used alone for purchasing, humanitarian, or policy decisions.

## Project objectives

- Combine monthly food, exchange-rate, and energy-price records by market identifier and date.
- Inspect data coverage, duplicate keys, missingness, and price trends.
- Compare simple time-series baselines with initial machine-learning regressors.
- Explore a clearly labeled research definition of a month-over-month wheat-price increase greater than 5%.
- Document limitations and the next validation steps before any practical deployment.

## Data sources

The three source files are maintained by the World Bank Microdata Library. Download the exact release used by this notebook (`2026-03-24`) from the official catalog pages:

- **Food prices:** https://microdata.worldbank.org/catalog/4508
- **Exchange rates:** https://microdata.worldbank.org/catalog/6159
- **Energy prices:** https://microdata.worldbank.org/catalog/6133

The analyzed release covers January 2009 through March 2026 and has 5,175 rows in each of the three source tables. Each table has 25 `geo_id` values, including a `Market Average` series as well as named local markets.

**The source ZIP and CSV files are intentionally not included in this repository.** Download them from the official catalog pages and review the applicable terms before redistributing them. The notebook expects these exact filenames:

- `YEM_RTFP_mkt_2009_2026-03-24.zip`
- `YEM_RTFX_mkt_2009_2026-03-24.zip`
- `YEM_RTEP_mkt_2009_2026-03-24.zip`

## Quick start

### Option A — Google Colab (recommended for a first run)

1. Download the three ZIP archives from the official catalog links above. Keep the original filenames.
2. Open `Yemen_MarketShield_Initial_Analysis.ipynb` in Google Colab. You can upload the notebook to Colab from its **File → Upload notebook** menu.
3. Run the notebook from the first cell. When the data-upload cell prompts you, select all three ZIP files together.
4. Run the remaining cells in order. Review each output and warning; do not treat exploratory metrics as proof of real-world forecasting performance.

### Option B — Local Jupyter

1. Install Python 3.10 or newer.
2. Create and activate a virtual environment if desired.
3. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```

4. Place the three source ZIP files in the same directory as the notebook, keeping the filenames shown above.
5. Start Jupyter and run the notebook from top to bottom.

## Workflow in the notebook

1. Load the three ZIP archives and parse monthly dates.
2. Check date ranges, market coverage, and duplicate `(geo_id, price_date)` keys.
3. Merge a selected set of variables across the three datasets.
4. Plot the estimated monthly wheat-price series for `Market Average`.
5. Compare the previous-month baseline, a random-forest regressor, and a gradient-boosting model using a time-based split (training before January 2022; test from January 2022 onward).
6. Evaluate an experimental classifier for a greater-than-5% increase in the next month. This threshold is an exploratory choice, not an official crisis definition.

## Preliminary evaluation

These metrics were produced by running the current notebook against the source ZIP files available for this project. Treat them as **initial, dataset-specific results** pending further validation.

### Wheat-price regression on the temporal test set

| Model | MAE | RMSE | WAPE |
|---|---:|---:|---:|
| Previous-month baseline | 22.379 | 38.425 | 3.8% |
| Random forest — price level | 66.865 | 101.874 | 11.4% |
| Gradient boosting — price change | 27.469 | 42.989 | 4.7% |

The previous-month baseline performed better on all three listed metrics. The current experiments therefore do **not** show an improvement over this simple baseline.

### Experimental price-increase classification

| Metric | Result |
|---|---:|
| Training records | 3,900 |
| Test records | 1,250 |
| Positive rate in test set | 12.8% |
| Balanced accuracy | 0.614 |
| Precision | 0.193 |
| Recall | 0.588 |
| F1 | 0.291 |
| ROC-AUC | 0.660 |

At the current 0.5 threshold, low precision indicates many false alerts. This experiment is not ready for an operational early-warning system.

## Limitations and responsible use

- `c_wheat` is a monthly close estimate in the World Bank dataset, not necessarily an independently confirmed observed price. The source may combine direct observations with machine-learning estimates for missing values.
- The greater-than-5% label is a research definition, not an official definition of a food-security crisis.
- The evaluation is temporal but does not yet establish transfer to entirely unseen markets or independent observed-price records.
- Forecasting accuracy may vary by product, market, period, currency, and the quality or coverage of inputs.
- Threshold selection, probability calibration, missing-data analysis, robustness tests, and independent validation are needed before any decision-support deployment.
- Do not use the model alone to make humanitarian, financial, purchasing, or public-policy decisions.

## Repository layout

```text
Yemen-MarketShield-AI/
├── README.md
├── Yemen_MarketShield_Initial_Analysis.ipynb
├── requirements.txt
├── .gitignore
└── docs/
    ├── DATA_SOURCES.md
    └── PROJECT_REPORT.md
```

## Next milestones

1. Separate directly observed prices from model-estimated values and document each variable using the official metadata.
2. Evaluate against appropriate observed records where a fair comparison is possible.
3. Test multiple pre-specified thresholds, such as 3%, 5%, and 10%, and report precision–recall tradeoffs.
4. Test generalization to markets excluded from training.
5. Add reproducibility metadata, error analysis, and a clear model card before expanding the prototype.

## Author and Acknowledgements

Yemen MarketShield AI is an early-stage machine-learning research project developed in the context of the Professional AI Engineering Program (PAEP).

I would like to express my sincere gratitude to Dr. Khaled Al-Husseini for leading the program and to Eng. Umair Al-Baadani for his instruction and guidance.

This project represents an effort to apply machine-learning concepts to a real-world challenge relevant to Yemen. The current version is a research prototype, and further validation is required before practical deployment.