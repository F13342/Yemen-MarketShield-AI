# Yemen MarketShield AI — Corrected Experiment

**Experiment date:** 2026-10-22  
**Status:** Research / experimental; not production-ready.

## Objective

Predict whether the retail wheat price in a market will rise by strictly more than 5% in the following calendar month.

## Data and evaluation

- Original price records: 936.
- Markets represented in the original data: 23.
- Rows with known targets: 875.
- Rolling-origin alert-policy evaluation: 535 market-month cases.
- Actual rises in that evaluation: 82.
- Months evaluated with an available threshold: 39.

## Model comparison

The following results use a policy that selects approximately the highest-scoring 30% of markets in each evaluated month.

| Metric | Logistic Regression | LightGBM | Previous-month-change baseline |
|---|---:|---:|---:|
| Alerts | 174 | 174 | 174 |
| True positives | 34 | 33 | 32 |
| False positives | 140 | 141 | 142 |
| False negatives | 48 | 49 | 50 |
| Pooled precision | 19.54% | 18.97% | 18.39% |
| Pooled recall | 41.46% | 40.24% | 39.02% |
| Pooled F1 | 26.56% | 25.78% | 25.00% |
| Mean monthly ROC-AUC | 0.5934 | 0.5981 | 0.5195 |
| Mean monthly Average Precision | 0.3994 | 0.3982 | 0.3871 |

These differences do not establish that one model is statistically superior. The preliminary confidence intervals for the monthly precision, recall, and F1 differences included zero.

## October 2026 research forecast

The experimental forecast uses September 2026 observed prices for markets with available data. Scores are model scores, not calibrated probabilities. A score below the experimental threshold does not guarantee that prices will not rise.

## Artifacts

- `Yemen_MarketShield_Corrected.ipynb` — experiment notebook.
- `results/marketshield_corrected_outputs/model_selection_report_ar.md` — Arabic model-selection report.
- `results/marketshield_corrected_outputs/figures/` — six generated figures.
- CSV files — monthly panel, labels, predictions, model comparisons, threshold-policy evaluations, and October research forecast.
- `marketshield_price_only_model.joblib` — saved price-only model.

## Limitations

- False positives remain high.
- The evaluation contains a limited number of positive cases.
- Results are retrospective and do not guarantee future performance.
- Risk scores should not be interpreted as calibrated probabilities.
- The experiment is not approved for operational economic alerts.
- Future evaluation should use genuinely new data and preserve the information available at each forecast date.

## Reproducibility

Run the notebook in a compatible Python environment and verify that the required source files and dependencies are available. Review the notebook code and source-data provenance before treating the outputs as independently reproducible.
