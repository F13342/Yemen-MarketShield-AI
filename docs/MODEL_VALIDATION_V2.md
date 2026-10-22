# Yemen MarketShield AI — Model Improvement and Temporal Validation Report

**Status:** Research prototype — not approved for operational, humanitarian, purchasing, or policy decisions.

## 1. Research Question and Target Definition

The classifier predicts whether the next consecutive month's `c_wheat` close estimate rises by more than 5% compared with the current month's estimate. This is an exploratory statistical event defined for this project; it is not an official food-crisis or shortage label. The input source is the World Bank Real-Time Food Prices release dated 2026-03-24, with price dates from January 2009 through March 2026 across 24 local markets after excluding the `Market Average` aggregate.

The source series combines direct market data with model-estimated missing values and is subject to revision. See the World Bank dataset documentation: https://microdata.worldbank.org/catalog/4508.

## 2. Data and Temporal Split Controls

- The three source archives each contain 5,175 market-month rows. Keys `(geo_id, price_date)` match across food, exchange-rate, and energy files without duplicates.
- The merged analytical table contains 5,175 rows and 39 selected columns before excluding the aggregate.
- The model table contains 4,944 consecutive next-month examples over 24 local markets; overall target event rate is approximately 18.3%.
- Prequential predictions span from origin month December 2018 through February 2026, yielding 2,088 predictions (87 forecast-origin months x 24 markets).
- At each origin month, training rows are restricted to records whose next-month target is already known by that origin, reducing target-time leakage.
- Thresholds are selected by maximizing F1 on target months January 2019 through December 2021 and frozen for target months January 2022 through March 2026.

**Independence caveat:** The later period was examined in earlier project experiments, making this a stricter retrospective walk-forward replay rather than a completely untouched independent holdout.

## 3. Regression Benchmark Results

A supplementary expanding-window backtest across selected calendar years (2015, 2017, 2019, 2021, 2023, 2024, and 2025; 24 local markets) produced the following results:

| Model | Mean MAE | Mean RMSE | Mean WAPE (%) |
|-------|--------:|----------:|--------------:|
| Previous-month baseline | 15.860 | 26.448 | 4.180 |
| Gradient Boosting on log change | 19.628 | 30.368 | 5.066 |
| Mean of last 3 months | 23.256 | 35.586 | 6.067 |
| Blend (75% lag-1 + 25% lag-12) | 24.369 | 34.928 | 6.469 |
| LightGBM on log price | 31.104 | 51.472 | 8.079 |
| Seasonal naive (12 months) | 65.691 | 89.141 | 17.831 |
| Ridge log-price | 120.744 | 227.082 | 26.334 |

These results do not demonstrate that the tested ML regressors improve upon the simple previous-month baseline.

## 4. Classification Results: Core Versus Expanded Features

Both variants use 60-estimator LightGBM with identical monthly prequential fitting protocols. The **core** features include current/lagged prices, changes, and seasonality (73 numeric features plus market ID). The **expanded** variant adds lagged confidence, data-coverage, and interpolation indicators (101 numeric features plus market ID). Thresholds are selected separately for each model by maximum F1 on the validation period, with precision as the tie-breaker.

| Model / Split | Threshold | ROC-AUC | Avg. Precision | Precision | Recall | F1 | Bal. Accuracy | Alerts | TP | FP | FN | TN |
|---------------|----------:|--------:|---------------:|----------:|-------:|---:|--------------:|-------:|---:|---:|---:|---:|
| Core — validation | 0.475 | 0.749 | 0.474 | 0.435 | 0.670 | 0.528 | 0.717 | 285 | 124 | 161 | 61 | 518 |
| Core — later replay | 0.475 | 0.684 | 0.219 | 0.224 | 0.555 | 0.319 | 0.638 | 384 | 86 | 298 | 69 | 771 |
| Expanded — validation | 0.500 | 0.747 | 0.480 | 0.459 | 0.611 | 0.524 | 0.707 | 246 | 113 | 133 | 72 | 546 |
| Expanded — later replay | 0.500 | 0.680 | 0.218 | 0.223 | 0.510 | 0.310 | 0.626 | 355 | 79 | 276 | 76 | 793 |

The core model maintains a marginal advantage by both validation F1 and later-replay F1. Adding confidence/coverage features does not deliver a net improvement. On the later replay, approximately **77.6% of core-model alerts** and **77.7% of expanded-model alerts** are false positives. The target event prevalence shifts from 21.4% in validation to 12.7% in the later period, contributing to the performance degradation.

A simple momentum rule (flagging current-month increases exceeding 5%) achieves later-replay precision 0.212, recall 0.226, and F1 0.219 with 165 alerts. The LightGBM model identifies more positive events but primarily by issuing more warnings. Whether this trade-off is worthwhile requires domain-specific elicitation of false-alarm and missed-event costs.

## 5. External Data Audit

An external data source was identified for post-vintage observations: the Yemen Ministry of Industry, Trade and Investment public price list (issued 17 September 2026) reports weekly wheat-grain and wheat-flour prices for 20 August through 17 September 2026. Source: https://moit.gov.ye/complaints/prices.

The observations are archived in `docs/independent_external_audit_moit_weekly_prices.csv`. They do not constitute a quantitative validation of this model because they are weekly entries with different product-unit definitions, do not expose the same 24 market-month keys, and are not directly aligned with the model's target.

The most promising structured candidate for independent evaluation is the **WFP Food Prices series through HDX HAPI**: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/.

## 6. Conclusions and Next Steps

1. The model is not operationally ready. At current thresholds, the majority of warnings are false positives.
2. Model and threshold should only be frozen after defining acceptable alert burden with domain users.
3. At least 6–12 months of independent observed per-market data should be obtained for external validation.
4. Future evaluation should employ rolling-origin methodology, compare all models on identical rows, and report uncertainty intervals and per-market performance.
5. Probability calibration and threshold analysis should be confined to validation data only.

**Current decision:** Research prototype and shadow-testing candidate only. No model outputs should inform real-world humanitarian, purchasing, financial, or public warning decisions.
