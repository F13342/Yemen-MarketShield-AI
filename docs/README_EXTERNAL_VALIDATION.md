# WFP External Temporal Experiment

## Overview

The notebook `Yemen_MarketShield_WFP_External_Validation.ipynb` implements a separate temporal experiment using actual retail wheat prices from the World Food Programme's HDX HAPI data service. The notebook is compatible with both local VS Code/Jupyter environments and Google Colab.

## Input Requirements

| File | Description |
|------|-------------|
| `WFP_Wheat_Yemen_HAPI_Response.json` | HAPI response snapshot for Yemen wheat (commodity code 84), actual retail prices, YER/kg |
| `YEM_RTFP_mkt_2009_2026-03-24.zip` | World Bank food-price archive for historical comparison |

For local execution, place both files alongside the notebook. For Google Colab, upload the files when prompted.

## Output

The notebook generates seven CSV result files in `results/` and a convenience archive `Yemen_MarketShield_WFP_Validation_Outputs.zip`.

## Methodological Notes

- HAPI observations are filtered to actual retail wheat prices denominated in YER/kg.
- Historical comparison is approximate: HAPI reference periods run from the 15th to the 14th and are mapped to their start calendar month.
- Potential upstream data overlap with World Bank historical values means this comparison is descriptive, not independent validation.
- The April–September 2026 test set contains 62 one-period-ahead observations across 11 markets.
- The warning classifier identifies only 6 positive events and produces 50 false alarms; the result is a research comparison only.
