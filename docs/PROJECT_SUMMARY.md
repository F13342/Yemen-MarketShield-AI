# Project Summary — Yemen MarketShield AI

## 1. Scope

This submission package contains two research experiments investigating the predictability of monthly wheat price fluctuations in Yemen. The experiments address related but distinct targets and are reported separately.

## 2. Experiment A — World Bank Monthly Walk-Forward Replay

**Data source:** World Bank Real-Time Food Prices release dated 24 March 2026, supplemented with exchange-rate and energy price archives.

**Coverage:** January 2009 through March 2026; 24 local markets modeled after excluding the `Market Average` aggregate series.

**Target:** Binary classification — whether the next consecutive month's `c_wheat` close estimate exceeds the current month by more than 5%.

**Experimental design:**
- Total predictive examples: 4,944 valid consecutive-month rows
- Prequential output: 2,088 market-origin predictions (87 forecast-origin months x 24 markets)
- Validation split: 864 rows (target months January 2019 through December 2021)
- Later-period replay: 1,224 rows (target months January 2022 through March 2026)
- Models: LightGBM with 73 core features versus 101 expanded features (including data-quality indicators)
- Thresholds selected exclusively on the validation period: 0.475 (core) and 0.500 (expanded)

### Classification Results

| Model / Split | ROC-AUC | AP | Precision | Recall | F1 | Alerts | TP | FP | FN | TN |
|---------------|--------:|---:|----------:|-------:|---:|-------:|---:|---:|---:|---:|
| Core — validation | 0.749 | 0.474 | 0.435 | 0.670 | 0.528 | 285 | 124 | 161 | 61 | 518 |
| Core — later replay | 0.684 | 0.219 | 0.224 | 0.555 | 0.319 | 384 | 86 | 298 | 69 | 771 |
| Expanded — validation | 0.747 | 0.480 | 0.459 | 0.611 | 0.524 | 246 | 113 | 133 | 72 | 546 |
| Expanded — later replay | 0.680 | 0.218 | 0.223 | 0.510 | 0.310 | 355 | 79 | 276 | 76 | 793 |

**Interpretation:** The expanded data-quality features did not improve later-period F1. False alert rates were approximately 77.6% for the core model and 77.7% for the expanded model. A simple prior-month momentum rule achieved a later-replay F1 of approximately 0.219 with fewer total alerts but lower recall.

## 3. Experiment B — WFP HAPI Actual-Price Temporal Experiment

**Input:** 936 HAPI records filtered to actual retail wheat prices in YER/kg across 23 markets, with reference periods from December 2021 through September 2026.

**Historical comparison:** 851 matched market-period pairs (January 2022 through March 2026) yielded MAE 18.20 YER/kg, RMSE 46.29, WAPE 2.71%, and Pearson correlation 0.9879.

**Future test:** 62 one-period-ahead observations from April through September 2026 across 11 markets.

### Regression Results

| Model | Test Rows | MAE (YER/kg) | RMSE | WAPE |
|-------|----------:|-------------:|-----:|-----:|
| Previous-period baseline | 62 | 20.00 | 33.94 | 2.41% |
| Gradient Boosting | 62 | 24.68 | 32.58 | 2.97% |
| Random Forest | 62 | 28.28 | 38.90 | 3.41% |
| Seasonal naive (12 months) | 62 | 217.43 | 269.28 | 26.19% |

### Warning Classifier Results

The exploratory greater-than-5% rise classifier produced: precision 9.1%, recall 83.3%, F1 0.164, ROC-AUC 0.479, with only 6 positive events among 62 test rows and 50 false positives.

## 4. Limitations

1. The later World Bank period was examined in earlier project experiments and does not constitute an untouched holdout.
2. World Bank estimates may include model-imputed values and are subject to revision.
3. WFP and World Bank historical matching is approximate and may share upstream data provenance; historical agreement is therefore descriptive, not independent validation.
4. The WFP future test window has been analyzed and cannot be treated as an untouched holdout for further model selection.
5. Neither experiment establishes operational utility; predictions must not be used for humanitarian allocation, procurement, finance, or public warnings.

## 5. Recommended Next Steps

Lock the target definition, acceptable false-alarm burden, feature set, and thresholds with a domain reviewer. Record predictions before receiving new test data or verified independent observations. Align commodity, geography, currency, unit, and time horizon before any external comparison. Report uncertainty intervals and per-market performance. Maintain any future trial in silent/shadow mode with human review.
