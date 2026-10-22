# WFP External Temporal Experiment

The notebook `Yemen_MarketShield_WFP_External_Validation.ipynb` is the second, separate experiment in this package. It runs in local VS Code/Jupyter and Google Colab. For local runs, keep `WFP_Wheat_Yemen_HAPI_Response.json` and `YEM_RTFP_mkt_2009_2026-03-24.zip` alongside the notebook. Colab prompts for these two files.

It generates seven CSV results in `results/` and a convenience archive `Yemen_MarketShield_WFP_Validation_Outputs.zip`.

The HAPI observations are filtered to actual retail wheat prices denominated in YER/kg. The historic comparison is approximate because HAPI reference periods run 15th-to-14th and are mapped to their start calendar month. Potential upstream data overlap with World Bank historical values means this is not claimed as fully independent-source validation.

The April–September 2026 test contains 62 one-period-ahead observations across 11 markets. The warning classifier has only six positive cases and issues many false alarms. The result is a research comparison only; do not use for operational warning decisions.
