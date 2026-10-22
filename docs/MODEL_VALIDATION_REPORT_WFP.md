# Yemen MarketShield AI — WFP Temporal Validation Report

**Status:** Research validation only — not an operational early-warning system.  
**Analysis date:** 21 October 2026.

## 1. HAPI Response Description

The supplied HDX HAPI response contains **936 records** for commodity code `84` (Wheat) across **23 markets**. All returned records satisfy the following criteria:

- `price_flag = actual` (monthly collected price data per HAPI terminology)
- `price_type = Retail`
- `currency_code = YER`
- `unit = KG`

The earliest `reference_period_start` is **15 December 2021** and the latest is **15 September 2026**, with the latest `reference_period_end` being **14 October 2026**. The result contains no duplicate `(market_code, commodity_code, reference_period_start)` keys. The 23 returned WFP markets correspond to 23 market names in the World Bank food-price file.

## 2. Historical Cross-Dataset Comparison

Each HAPI reference period was matched to the World Bank monthly row for the same market and the calendar month of `reference_period_start`. This comparison was restricted to January 2022 through March 2026.

| Metric | Result |
|--------|-------:|
| Matched market-month pairs | 851 |
| Markets represented | 23 |
| MAE | 18.20 YER/kg |
| RMSE | 46.29 YER/kg |
| WAPE | 2.71% |
| Pearson correlation | 0.9879 |
| Mean bias (HAPI minus World Bank) | +2.65 YER/kg |

The high correlation and low relative error indicate close historical agreement under this approximate month mapping. However, this does not constitute independent validation, as the data sources may share upstream provenance.

**References:**
- HDX HAPI Food Prices: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/
- HDX HAPI price flags: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/enums/
- World Bank RTP methodology: https://documents1.worldbank.org/curated/en/099430004232434765/pdf/IDU-8a5b9997-4299-4e50-ac10-b25f11061d21.pdf

## 3. Temporal Split Protocol

The WFP HAPI price series was treated as the target for a new benchmark experiment. This is a separate WFP-series experiment, not a claim that the original World Bank-trained model has passed independent-source validation.

- **Training period:** Before April 2025
- **Validation period:** April 2025 through March 2026
- **Test period:** April through September 2026
- **Target:** Next monthly WFP actual retail wheat price in YER/kg, by market
- **Features:** Previous calendar-month values (lags 1, 2, 3, 6, and 12 where available), prior change, market identity, and calendar seasonality
- **Evaluation:** Rolling one-period-ahead predictions

The test set comprises 63 raw records, of which **62** have a previous calendar-month observation and can be evaluated across **11 markets**.

## 4. Regression Results

Model selection was performed on the validation period using 100 common validation rows. On that validation set, the previous-period baseline achieved MAE **80.970 YER/kg**, compared with **85.266** for Gradient Boosting and **85.827** for Random Forest.

### Test Period Results (April–September 2026)

| Model | Test Rows | Markets | MAE (YER/kg) | RMSE (YER/kg) | WAPE |
|-------|----------:|--------:|-------------:|---------------:|-----:|
| Previous-period price | 62 | 11 | 20.00 | 33.94 | 2.41% |
| Gradient Boosting | 62 | 11 | 24.68 | 32.58 | 2.97% |
| Random Forest | 62 | 11 | 28.28 | 38.90 | 3.41% |
| Seasonal naive (12 months) | 62 | 11 | 217.43 | 269.28 | 26.19% |

The previous-period baseline achieves the best MAE and WAPE. Gradient Boosting shows slightly lower RMSE, suggesting fewer large squared errors, but its typical absolute error and weighted percentage error are worse.

## 5. Warning Classifier Results

The target label is whether the current WFP actual price exceeds the immediately previous month's price by more than 5%. The Logistic Regression threshold was selected on the validation period by maximizing F1, then frozen for the test period.

| Metric | Result |
|--------|-------:|
| Test rows | 62 |
| Actual positive events | 6 (9.7%) |
| Selected threshold | 0.49 |
| Precision | 9.1% |
| Recall | 83.3% |
| F1 | 0.164 |
| Balanced accuracy | 0.470 |
| ROC-AUC | 0.479 |
| Average precision | 0.131 |

**Confusion matrix:** TN=6, FP=50, FN=1, TP=5

The extremely small number of positive events (6) renders these classification metrics highly uncertain. The model produces an excessive number of false alarms, and the ROC-AUC falls below 0.5 in this test, indicating performance worse than random for this particular sample.

## 6. Conclusions and Recommendations

1. MarketShield is not an operational early-warning system.
2. The April–September 2026 window has been examined and is no longer untouched for future tuning decisions. Subsequent model iterations must evaluate on new, later data releases.
3. Future work should explore improved feature sets (exchange rate and fuel prices, contingent on availability at forecast time), alternative target definitions, market-specific calibration, and rolling-origin backtests.
4. Separate source verification is required before claiming independence from WFP observations.
5. Raw data licensing terms must be reviewed before public distribution.

**Conclusion:** The WFP data file provides useful temporal evaluation context, but this analysis does not demonstrate that the alert classifier or ML regressors are ready for operational deployment.
