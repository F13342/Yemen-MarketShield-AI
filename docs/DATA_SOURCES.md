# Data Sources and Provenance

## Primary Data

This project uses monthly Yemen Real-Time Prices (RTP) data from the World Bank Microdata Library. The analyzed release is dated `2026-03-24` and covers January 2009 through March 2026.

| Dataset | Official Catalog | Archive Filename | Rows |
|---------|------------------|------------------|-----:|
| Food prices | https://microdata.worldbank.org/catalog/4508 | `YEM_RTFP_mkt_2009_2026-03-24.zip` | 5,175 |
| Exchange rates | https://microdata.worldbank.org/catalog/6159 | `YEM_RTFX_mkt_2009_2026-03-24.zip` | 5,175 |
| Energy prices | https://microdata.worldbank.org/catalog/6133 | `YEM_RTEP_mkt_2009_2026-03-24.zip` | 5,175 |

## Supplementary Data

| Source | Description | Usage |
|--------|-------------|-------|
| WFP HDX HAPI | 936 actual retail wheat price records (YER/kg), 23 markets | Temporal validation experiment |
| Yemen Ministry of Industry and Trade | Weekly wheat prices (August–September 2026) | External audit reference |
| FAO/GIEWS Country Brief | Contextual market and food-security information | Background reference |

## Processing Notes

- The merge key is `(geo_id, price_date)`.
- Each table has zero duplicate keys; all three tables share identical key sets (5,175 keys).
- The merged working table retains selected food, exchange-rate, energy, market-location, and confidence/coverage features.
- `Market Average` is included as an aggregate series and is excluded from market-level modeling.
- Input archives are not committed to the public repository pending source redistribution review.

## Interpretation Note

The RTP data may combine directly observed prices with model estimates for missing observations. Variables prefixed with `c_` (e.g., `c_wheat`) represent estimated monthly close values. They should not be interpreted as independently verified physical market observations without additional validation against external sources.
