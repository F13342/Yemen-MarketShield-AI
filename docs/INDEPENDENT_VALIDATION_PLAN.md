# Independent Temporal Validation Plan — Yemen MarketShield AI

## Purpose

The current LightGBM experiment can be replayed monthly without allowing training labels whose next-month result is not yet known. However, target dates from 2022 onward were inspected earlier in development, and the World Bank release is retrospective and revisable. A truly independent test therefore remains open.

## External data found

1. **Yemen Ministry of Industry, Trade and Investment — price list**: https://moit.gov.ye/complaints/prices
   - The page states that the current posted list was issued 17 September 2026 and includes weekly price entries / trend values from 20 August to 17 September 2026.
   - Wheat grain listed per 50 kg: 11,200; 11,200; 11,200; 11,500; 11,400 YER.
   - Wheat flour listed per 50 kg: 14,000; 13,500; 13,700; 13,800; 13,500 YER.
   - The entries are archived in `independent_external_audit_moit_weekly_prices.csv`.
   - **Limit:** the observed table does not provide the same per-market monthly rows/fields as the World Bank model target. It cannot directly score existing local-market probabilities, but it can support qualitative and schema-alignment checks.
2. **FAO/GIEWS Yemen country brief**: https://www.fao.org/giews/countrybrief/country.jsp?code=YEM&lang=ar
   - Reference date 13 October 2026. It offers timely market and food-security context, but it is not a structured per-market monthly price series matching this model's target.
3. **WFP Food Prices through HDX HAPI**: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/
   - This is the strongest structured candidate to inspect next. Documented fields include commodity, price flag, price type, price, unit, currency, reference period, market code/name and administrative geography. The series is primarily monthly and updated weekly.
   - HAPI requests require an `app_identifier` generated through its setup workflow: https://hdx-hapi.readthedocs.io/en/latest/getting-started/. Generate/use it privately and do not commit access identifiers into the public repository.
   - Where available, separate actual source observations from aggregated or imputed data using the price flag and document all filtering decisions.
   - **Provenance gate:** verify whether records overlap with the World Bank series or its upstream estimation pipeline. If they overlap, treat WFP as a comparison series rather than fully independent ground truth.

## Minimum requirements before scoring a new independent test

- Product is the same commodity (grain wheat vs wheat flour must not be mixed).
- Units and currency are normalized (for example, YER/kg from YER/50kg, preserving source precision).
- Data rows contain market/location, observation period, price and source/collection method.
- Observation date is later than the World Bank vintage cutoff, or comes from a verified pre-forecast point-in-time archive.
- Predictions are recorded before external outcomes arrive. Do not refit or reselect thresholds after seeing the test outcomes.
- Evaluate the *same horizon and event definition*, or explicitly define a separate external validation target. A weekly price movement is not interchangeable with a monthly next-price increase.
- Report alert count, precision, recall, missed events, false alerts, uncertainty, and market-wise performance. If sufficient observations are unavailable, report “not enough matched data” rather than forcing a score.

## Proposed locked protocol

1. Keep the current World Bank-trained model and selected threshold frozen as a candidate, not the operational choice.
2. Obtain and freeze a separate observed market dataset/version not used for model construction.
3. Map product, market, unit and dates; document unmatched observations before evaluating results.
4. Produce predictions before unlocking the outcome period.
5. Have a reviewer who did not tune the model run the scoring script against the frozen labels.
6. Decide whether the model improves over the prior-month baseline and a simple momentum rule using pre-defined acceptable false-alarm burden.
7. Until the matched external dataset exists and passes this protocol, retain research-only status.
