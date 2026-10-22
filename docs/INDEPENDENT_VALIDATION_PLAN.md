# Independent Temporal Validation Plan

## 1. Purpose

The current LightGBM experiment can be replayed monthly without allowing training labels whose next-month result is not yet known. However, target dates from 2022 onward were examined during earlier development, and the World Bank release is retrospective and revisable. A truly independent test therefore remains an open requirement.

## 2. Identified External Data Sources

### 2.1 Yemen Ministry of Industry, Trade and Investment

**Source:** https://moit.gov.ye/complaints/prices

The posted price list (issued 17 September 2026) includes weekly price entries for 20 August through 17 September 2026:
- Wheat grain per 50 kg: 11,200; 11,200; 11,200; 11,500; 11,400 YER
- Wheat flour per 50 kg: 14,000; 13,500; 13,700; 13,800; 13,500 YER

These entries are archived in `independent_external_audit_moit_weekly_prices.csv`. **Limitation:** The data does not provide per-market monthly rows matching the World Bank model target. It supports qualitative and schema-alignment checks only.

### 2.2 FAO/GIEWS Yemen Country Brief

**Source:** https://www.fao.org/giews/countrybrief/country.jsp?code=YEM&lang=ar

Reference date: 13 October 2026. Provides contextual market and food-security information but is not a structured per-market monthly price series.

### 2.3 WFP Food Prices through HDX HAPI

**Source:** https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/

This is the strongest structured candidate for independent evaluation. Documented fields include commodity, price flag, price type, price, unit, currency, reference period, market code/name, and administrative geography.

**Provenance requirement:** Verify whether records overlap with the World Bank series or its upstream estimation pipeline. If overlap exists, treat WFP as a comparison series rather than fully independent ground truth.

## 3. Minimum Requirements Before Scoring

- Product is the same commodity (wheat grain versus wheat flour must not be mixed)
- Units and currency are normalized (e.g., YER/kg from YER/50kg)
- Data rows contain market/location, observation period, price, and source/collection method
- Observation date is later than the World Bank vintage cutoff, or comes from a verified pre-forecast archive
- Predictions are recorded before external outcomes arrive
- The same horizon and event definition are evaluated, or a separate validation target is explicitly defined
- Report alert count, precision, recall, missed events, false alerts, uncertainty, and per-market performance

## 4. Proposed Validation Protocol

1. Freeze the current World Bank-trained model and selected threshold as a candidate.
2. Obtain and freeze a separate observed market dataset not used in model construction.
3. Map product, market, unit, and dates; document unmatched observations before evaluation.
4. Produce predictions before unlocking the outcome period.
5. Have a reviewer who did not tune the model execute the scoring script against frozen labels.
6. Compare model performance against the prior-month baseline and a simple momentum rule using pre-defined acceptable false-alarm criteria.
7. Until a matched external dataset passes this protocol, maintain research-only status.
