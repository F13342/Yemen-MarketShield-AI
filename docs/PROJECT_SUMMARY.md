# Project Summary — Yemen MarketShield AI

## Scope

This submission package contains two research experiments around Yemen wheat prices. They address related but not identical targets and should be reported separately.

## Experiment A — World Bank monthly walk-forward replay

- Source: World Bank Real-Time Food Prices release dated 24 March 2026, with food, exchange-rate and energy archives.
- Coverage in the merged tables: January 2009–March 2026; 24 local markets are modelled after excluding `Market Average`.
- Target: a greater-than-5% increase in next-consecutive-month `c_wheat` close estimate.
- Predictive examples: 4,944 valid consecutive-month rows.
- Prequential output: 2,088 market-origin predictions (87 forecast-origin months × 24 markets), origins December 2018–February 2026.
- Split by target month: 864 validation rows (2019–2021) and 1,224 later-period replay rows (2022–March 2026).
- Model: monthly LightGBM core (73 numeric features plus market ID) versus expanded (101 numeric features plus market ID); the latter adds lagged quality/coverage indicators.
- Thresholds chosen only on validation: 0.475 core and 0.500 expanded.

| Model / split | ROC-AUC | AP | Precision | Recall | F1 | Alerts | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Core validation | 0.749 | 0.474 | 0.435 | 0.670 | 0.528 | 285 | 124 | 161 | 61 | 518 |
| Core later replay | 0.684 | 0.219 | 0.224 | 0.555 | 0.319 | 384 | 86 | 298 | 69 | 771 |
| Expanded validation | 0.747 | 0.480 | 0.459 | 0.611 | 0.524 | 246 | 113 | 133 | 72 | 546 |
| Expanded later replay | 0.680 | 0.218 | 0.223 | 0.510 | 0.310 | 355 | 79 | 276 | 76 | 793 |

Interpretation: extra data-quality features did not improve later-period F1. False alerts were around 77.6% for core and 77.7% for expanded. A simple prior-month momentum rule had a later-replay F1 of approximately 0.219, with 165 alerts (35 TP, 130 FP, 120 FN, 939 TN), versus more alerts for LightGBM. The relative costs of missed events and false alerts have not been elicited from domain users.

## Experiment B — WFP HAPI actual-price temporal experiment

- Input snapshot: 936 HAPI records filtered to actual retail wheat prices in YER/kg, 23 markets, reference-period starts December 2021–September 2026.
- Historical comparison with World Bank: 851 matched market-period pairs for January 2022–March 2026, 23 markets. Under approximate mapping by the calendar month of `reference_period_start`: MAE 18.20 YER/kg, RMSE 46.29, WAPE 2.71%, Pearson correlation 0.9879, mean bias +2.65 YER/kg.
- Future test: 62 one-period-ahead market observations from April–September 2026 across 11 markets; one missing-prior-month observation is excluded.

| Regression model | Test rows | MAE (YER/kg) | RMSE | WAPE |
|---|---:|---:|---:|---:|
| Previous period baseline | 62 | 20.00 | 33.94 | 2.41% |
| Gradient Boosting | 62 | 24.68 | 32.58 | 2.97% |
| Random Forest | 62 | 28.28 | 38.90 | 3.41% |
| Seasonal naive (12 months) | 62 | 217.43 | 269.28 | 26.19% |

The previous-period baseline had the best MAE and WAPE. Gradient Boosting had the lowest RMSE among the listed ML models but worse MAE and WAPE than the simple baseline.

The experimental >5% rise classifier had only 6 positive test events among 62 rows, selected threshold 0.49, precision 0.091, recall 0.833, F1 0.164, balanced accuracy 0.470, ROC-AUC 0.479 and average precision 0.131; confusion counts were TN=6, FP=50, FN=1, TP=5. The small event count and 50 false alarms make these results highly uncertain.

## Evidence limitations

1. The later World Bank period was viewed in earlier project experiments and is not an untouched holdout.
2. World Bank estimates may be revised and include model-estimated values. A retrospective dataset snapshot does not establish exactly what would have been known at each historical forecast origin.
3. HAPI/World Bank historical matching maps HAPI periods beginning on the 15th to the corresponding calendar month. This is approximate, and the two sources may share upstream data provenance; therefore historical agreement is descriptive, not independent validation.
4. The WFP future window April–September 2026 has already been analysed in this package and cannot be treated as an untouched future holdout for further model selection.
5. Neither model experiment establishes operational utility. Predictions must not be used for humanitarian allocation, procurement, finance or public warnings.

## Recommended next milestone

Lock the target, the acceptable false-alarm burden, features and thresholds with a domain reviewer; then record predictions before receiving a newly released test window or a verified independent observation source. Align commodity, geography, currency, unit and time horizon first. Report uncertainty and market-wise performance. Keep any future trial in silent/shadow mode with human review.
