# Yemen MarketShield AI — WFP Temporal Validation Note

**Status:** research validation only; not an operational early-warning system.
**Analysis snapshot:** 21 October 2026.
**Do not upload this validation package or raw data to the public GitHub repository without checking reuse/licensing terms.** It is intentionally separate from the project's public repository.

## 1. What is in the HAPI response?

The supplied HDX HAPI response contains **936 records** for commodity code `84` (`Wheat`) across **23 markets**. All returned records have:

- `price_flag = actual` (monthly collected price data in HAPI's terminology)
- `price_type = Retail`
- `currency_code = YER`
- `unit = KG`

The earliest `reference_period_start` is **15 December 2021** and the latest is **15 September 2026**, with the latest `reference_period_end` **14 October 2026**. The first period overlaps January 2022 even though its start falls in December 2021; HAPI's period is a 15th-to-14th interval. The result has no duplicate `(market_code, commodity_code, reference_period_start)` keys.

The 23 returned WFP markets match 23 market names in the World Bank food-price file. `Market Average` and `Haradh Town` do not appear in this HAPI response.

## 2. Historical cross-dataset agreement (not an independent-source test)

We matched each HAPI reference period to the World Bank monthly row for the same market and the **calendar month of `reference_period_start`**. We restricted this descriptive comparison to January 2022–March 2026, the overlap available in the supplied World Bank archive. This month mapping is an approximation: HAPI periods run from the 15th of one month to the 14th of the next.

| Metric | Result |
|---|---:|
| Matched market-month pairs | 851 |
| Markets represented | 23 |
| MAE | 18.20 YER/kg |
| RMSE | 46.29 YER/kg |
| WAPE | 2.71% |
| Pearson correlation | 0.9879 |
| Mean bias (HAPI minus World Bank `c_wheat`) | +2.65 YER/kg |

The high correlation and low relative error indicate close historical agreement under this approximate month mapping. They do **not** prove independent validation. HAPI describes this table as WFP's food-price series; World Bank Real-Time Prices methodology also uses underlying survey data from country systems, WFP and FAO and adds model estimates for missing observations. The data sources may therefore overlap in provenance.

References:
- HDX HAPI Food Prices & Market Monitor: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/
- HDX HAPI price flags and price types: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/enums/
- World Bank discussion of Real-Time Prices inputs/methodology: https://documents1.worldbank.org/curated/en/099430004232434765/pdf/IDU-8a5b9997-4299-4e50-ac10-b25f11061d21.pdf

## 3. Time-split protocol for WFP actual prices

We treated the WFP HAPI `price` series itself as the target for a new benchmark experiment. This is a **new WFP-series experiment**, not a claim that the original World Bank-trained MarketShield model has passed an independent-source test.

- **Training period:** before April 2025.
- **Validation period:** April 2025–March 2026.
- **Future test period:** April–September 2026.
- **Target:** the next monthly WFP actual retail wheat price in YER/kg, by market.
- **Features:** only previous calendar-month values (lags 1, 2, 3, 6 and 12 where available), prior change, market and calendar seasonality.
- Lags are joined by the exact market and calendar month; the code does not simply shift by row number.
- Evaluation is rolling one-period-ahead: once a prior period's price would be observable, it can be used for the next period's prediction. It is not a six-month forecast issued all at once.

There are 63 raw records in the April–September 2026 range; **62** have a previous calendar-month observation and can be evaluated as one-period-ahead forecasts across **11 markets**. One Taiz record is excluded because a prior monthly observation is missing. A few months/markets are missing in the source, so this is not a balanced panel.

## 4. Regression results

Model choice was assessed on the validation period, using 100 common validation rows where the 12-month seasonal naive comparator was available. On that validation set, the previous-period baseline achieved MAE **80.970 YER/kg**, versus **85.266** for Gradient Boosting and **85.827** for Random Forest. No tested ML regressor beat the simple baseline by MAE.

The models were then evaluated over the later test period (April–September 2026):

| Model | Test rows | Markets | MAE (YER/kg) | RMSE (YER/kg) | WAPE |
|---|---:|---:|---:|---:|---:|
| Previous-period price | 62 | 11 | 20.00 | 33.94 | 2.41% |
| Gradient Boosting | 62 | 11 | 24.68 | 32.58 | 2.97% |
| Random Forest | 62 | 11 | 28.28 | 38.90 | 3.41% |
| Seasonal naive (12 months earlier) | 62 | 11 | 217.43 | 269.28 | 26.19% |

The previous-period baseline has the best MAE and WAPE. Gradient Boosting has slightly lower RMSE, suggesting fewer very large squared errors in this small test, but its typical absolute error and WAPE are worse. This experiment therefore does not demonstrate a consistent advantage for machine learning.

## 5. Experimental warning classifier

The label is whether the current WFP actual price is more than 5% above the immediately previous calendar month's price. The Logistic Regression threshold was selected on the validation period by maximizing F1, then kept fixed for the test; the classifier itself was also kept fixed after the pre-validation training fit to avoid using validation/test labels to refit it.

| Test metric | Result |
|---|---:|
| Test rows | 62 |
| Actual rise cases | 6 (9.7%) |
| Threshold selected on validation | 0.49 |
| Precision | 9.1% |
| Recall | 83.3% |
| F1 | 0.164 |
| Balanced accuracy | 0.470 |
| ROC-AUC | 0.479 |
| Average precision | 0.131 |
| Confusion matrix (TN, FP, FN, TP) | (6, 50, 1, 5) |

Only six positive events occur in the test set, so these classification metrics are very uncertain. The model emits many false alarms; ROC-AUC is below 0.5 in this test. It is **not suitable for operational decisions**.

## 6. Decision and next work

1. Do not call MarketShield an operational early-warning system.
2. The April–September 2026 HAPI window has now been inspected, so it is no longer untouched for future tuning decisions. For a new model iteration, choose features/models/thresholds only on training/validation data, then evaluate on **new later releases** or a truly independent dataset.
3. Explore a better feature set (exchange rate and fuel only if their values would be known at forecast time), price-change/log-return targets, market-specific calibration, and rolling-origin backtests. Compare each against persistence baseline.
4. Obtain and verify a separate source or later data release for an external test; record whether it derives from WFP observations to avoid claiming source independence.
5. Review data license/terms before publicly committing raw WFP or World Bank records.

**Conclusion:** the WFP file is useful for future-period temporal evaluation, but this round does not show that the alert classifier or ML regressors are ready for real-world use.
