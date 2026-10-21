# Yemen MarketShield AI — Initial experiment report

**Status:** Research prototype / exploratory analysis  
**Dataset release:** 2026-03-24  
**Coverage:** January 2009–March 2026

## Research question

Can monthly food-price history together with exchange-rate and energy-price indicators help predict the recorded monthly wheat-price estimate or flag a possible greater-than-5% increase in the following month?

This is an exploratory machine-learning question, not an attempt to diagnose or officially classify food insecurity.

## Data validation

The three input tables each contain 5,175 rows. The shared keys are `(geo_id, price_date)`. The executed data checks found zero duplicate keys in each source table, matching key sets across all three tables, and 5,175 shared market-month keys. There are 25 `geo_id` values, including the `Market Average` aggregate.

## Regression experiment

The notebook uses a time-based split: records before January 2022 are used for training, and records from January 2022 onward are used for testing. Lagged price and indicator variables are used as predictors.

| Model | MAE | RMSE | WAPE |
|---|---:|---:|---:|
| Previous-month baseline | 22.379 | 38.425 | 3.8% |
| Random forest — price level | 66.865 | 101.874 | 11.4% |
| Gradient boosting — price change | 27.469 | 42.989 | 4.7% |

The previous-month baseline is the strongest of these three experiments across the reported metrics. This means the initial ML models have not demonstrated extra predictive value over the baseline.

## Experimental classifier

The target label is `1` where the next consecutive month's `c_wheat` is more than 5% above the current month's value. Only consecutive monthly pairs are retained. The 5% threshold is an exploratory threshold and is not an official food-crisis definition.

| Metric | Result at threshold 0.50 |
|---|---:|
| Training records | 3,900 |
| Test records | 1,250 |
| Positive rate — training | 20.3% |
| Positive rate — test | 12.8% |
| Balanced accuracy | 0.614 |
| Precision | 0.193 |
| Recall | 0.588 |
| F1 | 0.291 |
| ROC-AUC | 0.660 |

Confusion matrix at probability threshold 0.50, rows = actual class `[0, 1]`, columns = predicted class `[0, 1]`:

```text
[[698, 392],
 [ 66,  94]]
```

### Exploratory threshold sensitivity

The separate validation experiment fitted a validation model on records before January 2019 and compared probability thresholds on January 2019–December 2021. The threshold results were:

| Threshold | Balanced accuracy | Precision | Recall | F1 | False alarms | Missed increases | Correct warnings |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 0.25 | 0.506 | 0.218 | 0.617 | 0.322 | 428 | 74 | 119 |
| 0.35 | 0.523 | 0.231 | 0.508 | 0.317 | 327 | 95 | 98 |
| 0.45 | 0.533 | 0.244 | 0.430 | 0.311 | 257 | 110 | 83 |
| 0.50 | 0.540 | 0.255 | 0.399 | 0.311 | 225 | 116 | 77 |
| 0.60 | 0.550 | 0.275 | 0.352 | 0.309 | 179 | 125 | 68 |
| 0.70 | 0.550 | 0.298 | 0.280 | 0.289 | 127 | 139 | 54 |

At the illustrative threshold 0.35, the 2022-01 to 2026-02 test-period result was:

| Metric | Result at threshold 0.35 |
|---|---:|
| Balanced accuracy | 0.620 |
| Precision | 0.182 |
| Recall | 0.706 |
| F1 | 0.289 |
| ROC-AUC | 0.660 |

Confusion matrix:

```text
[[581, 509],
 [ 47, 113]]
```

Relative to threshold 0.50, threshold 0.35 detects 19 more positive cases and produces 117 more false alarms. Only 18.2% of alerts at the 0.35 threshold were correct. Because the test-period metrics at threshold 0.50 were examined earlier in this exploratory workflow, the threshold-0.35 results are a sensitivity follow-up rather than a completely untouched final evaluation. Any future model/threshold comparisons should use a fresh rolling-origin backtest or newly held-out period.

The classifier finds some positive cases, but precision is low and false alerts are numerous. It should not be deployed as a real-world warning system.


## Variable coverage and within-source sensitivity check

The following coverage was measured in the merged table (5,175 market-month rows):

| Variable | Non-missing | Missing | Coverage |
|---|---:|---:|---:|
| `wheat` | 2,273 | 2,902 | 43.92% |
| `c_wheat` | 5,175 | 0 | 100.00% |
| `fuel_diesel` | 1,890 | 3,285 | 36.52% |
| `c_fuel_diesel` | 5,175 | 0 | 100.00% |
| `exchange_rate_unofficial` | 1,752 | 3,423 | 33.86% |
| `c_exchange_rate_unofficial` | 5,175 | 0 | 100.00% |

The official data dictionary labels `c_wheat` as "Close estimate - Wheat". Where both `wheat` and `c_wheat` are non-missing (2,273 rows), they are exactly equal in 2,000 rows and differ in 273. Consequently, this comparison is treated as a within-source sensitivity check, not independent validation against ground truth.

For the January 2022–March 2026 test window, 1,275 rows remained in the evaluation table and 696 (54.59%) had a non-missing `wheat` value. Forecasts trained to predict `c_wheat` were compared with those `wheat` values on this subset:

| Model | MAE | RMSE | WAPE (%) |
|---|---:|---:|---:|
| Previous-month baseline | 27.157 | 48.628 | 4.230 |
| Random Forest | 77.751 | 115.300 | 12.112 |
| Gradient Boosting | 32.481 | 53.627 | 5.060 |

The previous-month baseline remains best on this comparison, but the semantic difference between `wheat` and `c_wheat` and the fact that they come from the same release limit what can be concluded. The result is not an independent ground-truth evaluation. The source-variable definition should be confirmed from the official [data dictionary](https://microdata.worldbank.org/catalog/4508/data-dictionary/YEM_2021_RTFP_MKT?file_name=YEM_RTFP_mkt_2009_2026-03-24.csv).

## Limitations

1. The price target is an estimated monthly close value from the RTP dataset, not necessarily a separately verified price observation.
2. The model evaluation has not yet been validated against an independent source of observed prices.
3. The evaluation is temporal, but the same markets can appear in training and testing; generalization to unseen markets is not established.
4. A positive month-to-month price change is not equivalent to food insecurity, a food crisis, or household-level harm.
5. The initial feature set, threshold, and model settings are exploratory and require robustness checks and pre-specified evaluation design.

## Recommended next steps

- Review the ticker and model-information files to understand variable definitions and confidence indicators.
- Clarify the relationship between `wheat` and `c_wheat` before treating either as ground truth.
- Add rolling-origin temporal evaluation and market-held-out evaluation.
- Assess alternative target definitions (for example, increases above 3%, 5%, or 10%) with pre-specified thresholds and report precision–recall curves and calibration.
- Seek an independent, well-documented price-validation source before any operational warning use.
- Document intended use, limitations, and failure modes before building a user-facing alert.

## Conclusion

The initial notebook establishes a reproducible data-joining and evaluation workflow. However, results do not currently justify claiming improved wheat-price forecasting or operational early-warning capability. The appropriate outcome at this stage is to publish the work as an early research prototype with transparent limitations and a clearly documented path to further validation.
