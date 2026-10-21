# Data sources and provenance

This project uses monthly Yemen Real-Time Prices (RTP) data from the World Bank Microdata Library. The notebook version analyzed here was downloaded as the release dated `2026-03-24` and covers `2009-01` through `2026-03`.

| Dataset | Official catalog | Expected archive filename | Rows in this release |
|---|---|---|---:|
| Food prices | https://microdata.worldbank.org/catalog/4508 | `YEM_RTFP_mkt_2009_2026-03-24.zip` | 5,175 |
| Exchange rates | https://microdata.worldbank.org/catalog/6159 | `YEM_RTFX_mkt_2009_2026-03-24.zip` | 5,175 |
| Energy prices | https://microdata.worldbank.org/catalog/6133 | `YEM_RTEP_mkt_2009_2026-03-24.zip` | 5,175 |

## Processing notes

- The merge key is `(geo_id, price_date)`.
- In the version tested for this repository, each table had zero duplicate keys and all three tables shared 5,175 keys.
- The merged working table retains selected food, exchange-rate, energy, market-location, and confidence/coverage features.
- `Market Average` is included as an aggregate series; it should not be treated as an ordinary local market in market-level interpretation.
- The input archives and derived CSV files are not committed to this repository. Users should download data from the official source and consult the terms and metadata there before redistribution.

## Important interpretation note

The RTP data may combine directly observed prices with estimates for missing data. In particular, `c_` variables such as `c_wheat` represent estimated monthly close values in this analysis. They should not be described as independently verified physical market observations without additional validation.
