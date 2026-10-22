# Yemen MarketShield AI — Initial Experiment Report

**Status:** Research prototype — exploratory analysis  
**Dataset release:** 2026-03-24  
**Coverage:** January 2009 through March 2026

## 1. Research Question

Can monthly food-price history, together with exchange-rate and energy-price indicators, help predict the recorded monthly wheat-price estimate or flag a possible greater-than-5% increase in the following month?

This is an exploratory machine learning question intended to investigate predictability patterns. It is not an attempt to diagnose or officially classify food insecurity.

## 2. Data Validation

The three input tables each contain 5,175 rows. The shared keys are `(geo_id, price_date)`. Validation checks confirmed zero duplicate keys in each source table, matching key sets across all three tables, and 5,175 shared market-month keys. There are 25 `geo_id` values, including the `Market Average` aggregate.

## 3. Regression Experiment

The notebook employs a temporal split: records before January 2022 constitute the training set, and records from January 2022 onward form the test set. Lagged price and indicator variables serve as predictors.

| Model | MAE | RMSE | WAPE |
|-------|----:|-----:|-----:|
| Previous-month baseline | 22.379 | 38.425 | 3.8% |
| Random Forest — price level | 66.865 | 101.874 | 11.4% |
| Gradient Boosting — price change | 27.469 | 42.989 | 4.7% |

The previous-month baseline outperforms both machine learning models across all reported metrics, indicating that the initial ML configurations have not demonstrated additional predictive value beyond the baseline.

## 4. Classification Experiment

The target label is `1` where the next consecutive month's `c_wheat` exceeds the current month's value by more than 5%. Only consecutive monthly pairs are retained. The 5% threshold is an exploratory definition and is not an official food-crisis classification.

| Metric | Result (threshold 0.50) |
|--------|------------------------:|
| Training records | 3,900 |
| Test records | 1,250 |
| Positive rate — training | 20.3% |
| Positive rate — test | 12.8% |
| Balanced accuracy | 0.614 |
| Precision | 0.193 |
| Recall | 0.588 |
| F1 | 0.291 |
| ROC-AUC | 0.660 |

### Confusion Matrix (threshold 0.50)

|  | Predicted 0 | Predicted 1 |
|---|---:|---:|
| **Actual 0** | 698 | 392 |
| **Actual 1** | 66 | 94 |

### Threshold Sensitivity Analysis

| Threshold | Balanced Accuracy | Precision | Recall | F1 | False Alarms | Missed Events | Correct Warnings |
|----------:|------------------:|----------:|-------:|---:|-----------:|-------------:|----------------:|
| 0.25 | 0.506 | 0.218 | 0.617 | 0.322 | 428 | 74 | 119 |
| 0.35 | 0.523 | 0.231 | 0.508 | 0.317 | 327 | 95 | 98 |
| 0.45 | 0.533 | 0.244 | 0.430 | 0.311 | 257 | 110 | 83 |
| 0.50 | 0.540 | 0.255 | 0.399 | 0.311 | 225 | 116 | 77 |
| 0.60 | 0.550 | 0.275 | 0.352 | 0.309 | 179 | 125 | 68 |
| 0.70 | 0.550 | 0.298 | 0.280 | 0.289 | 127 | 139 | 54 |

## 5. Variable Coverage Analysis

| Variable | Non-missing | Missing | Coverage |
|----------|----------:|--------:|---------:|
| `wheat` | 2,273 | 2,902 | 43.92% |
| `c_wheat` | 5,175 | 0 | 100.00% |
| `fuel_diesel` | 1,890 | 3,285 | 36.52% |
| `c_fuel_diesel` | 5,175 | 0 | 100.00% |
| `exchange_rate_unofficial` | 1,752 | 3,423 | 33.86% |
| `c_exchange_rate_unofficial` | 5,175 | 0 | 100.00% |

The `c_` prefixed variables represent close estimates and have complete coverage. The within-source sensitivity check on the 2,273 rows where both `wheat` and `c_wheat` are non-missing found exact equality in 2,000 rows and differences in 273 rows.

## 6. Limitations

1. The price target is an estimated monthly close value from the RTP dataset, not necessarily a separately verified price observation.
2. The model evaluation has not yet been validated against an independent external source of observed prices.
3. The evaluation is temporal, but the same markets appear in both training and testing; generalization to unseen markets is not established.
4. A positive month-to-month price change is not equivalent to food insecurity, a food crisis, or household-level harm.
5. The feature set, threshold, and model settings are exploratory and require robustness checks and pre-specified evaluation design.

## 7. Recommended Next Steps

- Clarify the relationship between `wheat` and `c_wheat` before treating either as ground truth.
- Implement rolling-origin temporal evaluation and market-held-out evaluation.
- Assess alternative target definitions (3%, 5%, 10% thresholds) with pre-specified decision boundaries.
- Obtain an independent, well-documented price-validation source before any operational use.
- Document intended use, limitations, and failure modes before constructing a user-facing interface.

## 8. Conclusion

The initial notebook establishes a reproducible data-joining and evaluation workflow. However, results do not currently justify claims of improved wheat-price forecasting or operational early-warning capability. The appropriate outcome at this stage is to publish the work as an early research prototype with transparent limitations and a documented path to further validation.
