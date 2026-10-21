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

| Metric | Result |
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

Confusion matrix at probability threshold 0.5, rows = actual class `[0, 1]`, columns = predicted class `[0, 1]`:

```text
[[698, 392],
 [ 66,  94]]
```

The classifier finds some positive cases, but precision is low and false alerts are numerous. It should not be deployed as a real-world warning system.

## Limitations

1. The price target is an estimated monthly close value from the RTP dataset, not necessarily a separately verified price observation.
2. The model evaluation has not yet been validated against an independent source of observed prices.
3. The evaluation is temporal, but the same markets can appear in training and testing; generalization to unseen markets is not established.
4. A positive month-to-month price change is not equivalent to food insecurity, a food crisis, or household-level harm.
5. The initial feature set, threshold, and model settings are exploratory and require robustness checks and pre-specified evaluation design.

## Recommended next steps

- Review the official metadata and variable documentation.
- Distinguish direct observations from model-derived estimates where the source supports it.
- Compare models against an independent observed-price validation set where possible.
- Add market-held-out evaluation and additional temporal backtests.
- Test multiple thresholds (for example, 3%, 5%, 10%) and report precision–recall curves and calibration.
- Document the model's intended use, limitations, and failure modes before building a user-facing alert.

## Conclusion

The initial notebook establishes a reproducible data-joining and evaluation workflow. However, results do not currently justify claiming improved wheat-price forecasting or operational early-warning capability. The appropriate outcome at this stage is to publish the work as an early research prototype with transparent limitations and a clearly documented path to further validation.
