# Yemen MarketShield AI — Model Improvement and Temporal Validation

**Status: research prototype only — not approved for operational, humanitarian, purchasing, or policy decisions.**

## 1. Question and target

The classifier predicts whether the next consecutive month's `c_wheat` close estimate rises by more than 5% compared with the current month's estimate. This is an exploratory statistical event defined for this project; it is **not** an official food-crisis or shortage label. The input source is the World Bank Real-Time Food Prices release dated 2026-03-24, with price dates from January 2009 through March 2026 across 24 local markets after excluding the `Market Average` aggregate.

The source series combines direct market data with model-estimated missing values and can be revised. See the World Bank dataset documentation: https://microdata.worldbank.org/catalog/4508. That makes the result useful for research but not equivalent to validating against independent transaction observations.

## 2. Data and time-split controls

- The three source archives each contain 5,175 market-month rows. Keys `(geo_id, price_date)` match across food, exchange-rate and energy files without duplicates.
- The merged analytical table contains 5,175 rows and 39 selected columns before excluding the aggregate.
- The model table contains 4,944 consecutive next-month examples over 24 local markets; overall target event rate is about 18.3%.
- Prequential predictions run from origin month December 2018 through February 2026, yielding 2,088 predictions (`87` forecast-origin months × `24` markets). Target months cover January 2019 through March 2026.
- At each origin month, training rows are restricted to records whose next-month target is already known by that origin. This reduces target-time leakage.
- Thresholds are selected by F1 on target months January 2019–December 2021 and frozen for target months January 2022–March 2026.

**Independence caveat:** the later period was inspected in earlier project experiments, so this is a stricter retrospective walk-forward replay, not a completely untouched independent holdout. The dataset is one retrospective vintage; it does not provide a complete archived point-in-time version of values as they were known at each historical origin.

## 3. Candidate regression results

A supplementary expanding-window backtest across selected calendar years (2015, 2017, 2019, 2021, 2023, 2024 and 2025; 24 local markets) found the previous-month estimate to be strongest on average.

| Model | Mean MAE | Mean RMSE | Mean WAPE (%) |
|---|---:|---:|---:|
| Previous-month baseline | 15.860 | 26.448 | 4.180 |
| Gradient boosting on log change | 19.628 | 30.368 | 5.066 |
| Mean of last 3 months | 23.256 | 35.586 | 6.067 |
| Blend 75% previous month + 25% previous year | 24.369 | 34.928 | 6.469 |
| LightGBM on log price | 31.104 | 51.472 | 8.079 |
| Seasonal naive (12 months) | 65.691 | 89.141 | 17.831 |
| Ridge log-price | 120.744 | 227.082 | 26.334 |

These are selected-window retrospective results, not an untouched benchmark. They do not show that the tested ML regressors improve on the simple baseline.

## 4. Early-warning classification: core versus expanded features

Both variants use 60-estimator LightGBM with the same monthly prequential fitting protocol. **Core** features include current/lagged prices, changes, and seasonality (73 numeric features plus market ID). **Expanded** adds lagged confidence, data-coverage and interpolation indicators (101 numeric features plus market ID). The threshold is selected separately for each model on the validation period by maximum F1, with precision as a tie-breaker.

| Model / split | Threshold | ROC-AUC | Average precision | Precision | Recall | F1 | Balanced accuracy | Alerts | TP | FP | FN | TN |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Core — validation | 0.475 | 0.749 | 0.474 | 0.435 | 0.670 | 0.528 | 0.717 | 285 | 124 | 161 | 61 | 518 |
| Core — later replay | 0.475 | 0.684 | 0.219 | 0.224 | 0.555 | 0.319 | 0.638 | 384 | 86 | 298 | 69 | 771 |
| Expanded — validation | 0.500 | 0.747 | 0.480 | 0.459 | 0.611 | 0.524 | 0.707 | 246 | 113 | 133 | 72 | 546 |
| Expanded — later replay | 0.500 | 0.680 | 0.218 | 0.223 | 0.510 | 0.310 | 0.626 | 355 | 79 | 276 | 76 | 793 |

The core model is marginally ahead by validation F1 and later-replay F1. Adding confidence/coverage features does not deliver a net improvement in these results. On later replay, approximately **77.6% of core-model alerts** and **77.7% of expanded-model alerts** are false positives. The event prevalence also changes from 21.4% in validation to 12.7% in the later period; that distribution shift hurts practical interpretation.

A simple momentum rule that flags a current-month increase greater than 5% has later-replay precision 0.212, recall 0.226 and F1 0.219 (165 alerts; 35 TP, 130 FP, 120 FN, 939 TN). The LightGBM model identifies more positives, but mostly by issuing more warnings. Whether that trade-off is worthwhile cannot be inferred from F1 alone: users of an actual early-warning service must define the relative costs of false alarms and missed events first.

## 5. Independent external-data audit — identified, not yet a matched evaluation

A separate source has observations after the World Bank data vintage: the Yemen Ministry of Industry, Trade and Investment public price list, issued 17 September 2026, reports weekly wheat-grain and wheat-flour prices for 20 August–17 September 2026. Source page: https://moit.gov.ye/complaints/prices. The five listed wheat-grain values per 50 kg are 11,200, 11,200, 11,200, 11,500 and 11,400 YER; wheat-flour values per 50 kg are 14,000, 13,500, 13,700, 13,800 and 13,500 YER.

The external observations are kept in `docs/independent_external_audit_moit_weekly_prices.csv`. They are **not** yet a quantitative validation of this model because they are weekly entries, do not expose the same 24 market-month keys in the retrieved table, use a 50 kg product-unit definition, and are not directly aligned with the model's next-month per-market `c_wheat` target. They are a useful source-discovery result, not evidence that the classifier forecasted these changes.

A more promising structured candidate is the **WFP Food Prices series through HDX HAPI**: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/. Its documentation lists commodity, price flag, price type, price, unit, currency, reference period, market code/name and administrative location; the series is primarily monthly and updated weekly. HAPI requests require an `app_identifier` created through its setup process (https://hdx-hapi.readthedocs.io/en/latest/getting-started/). Before calling this an independent holdout, verify it contains observations after March 2026, filter for actual collected observations where the price flag allows, align product/unit/market, and check whether WFP source rows overlap the World Bank estimates' upstream data. Do not claim independence until provenance has been checked.

Other contextual references include FAO/GIEWS Yemen country brief (reference date 13 October 2026): https://www.fao.org/giews/countrybrief/country.jsp?code=YEM&lang=ar and WFP's market-analysis/data portal: https://www.wfp.org/market-analysis. A matched independent test needs a machine-readable series with market, product, unit, observation date, price and source/methodology, ideally with a vintage available before each forecast.

## 6. Decision and next research steps

1. **Do not call the model operational-ready.** At current thresholds, most warnings are false positives; the label itself is an estimate-based proxy.
2. Freeze a model and decision threshold only after defining acceptable alert burden and missed-event cost with domain users.
3. Obtain at least 6–12 months of independent observed per-market data, or official historical snapshots recorded before each forecast. Align product, unit, currency, market, and time horizon first.
4. Run an untouched temporal test without inspecting results during model selection. Use rolling-origin evaluation, compare all models and baselines on the same rows, and report uncertainty intervals and per-market results.
5. Calibrate probabilities and analyze thresholds on validation data only. In any later pilot, run silent/shadow predictions with human review and no automated public or humanitarian alerts.

**Current decision:** research prototype / shadow-testing candidate only. No model outputs should be used to make real-world humanitarian, purchasing, financial or public warning decisions.
