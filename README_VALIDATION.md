# Yemen MarketShield AI — Validation Workbench

## Overview

This branch contains the validation workbench for the Yemen MarketShield AI project. It is maintained on a separate experimental branch (`experiment/validation-workbench`) and is designed to be reviewed independently before merging into the main branch.

## Contents

| File | Description |
|------|-------------|
| `Yemen_MarketShield_Model_Validation.ipynb` | Source-data merge, feature construction, monthly walk-forward methodology, threshold selection, and comparison of core versus expanded LightGBM variants |
| `marketshield_prequential_core_predictions.csv` | Per-market, per-origin predictions from the 73-feature core model |
| `marketshield_prequential_enhanced_predictions.csv` | Predictions from the 101-feature model incorporating data-quality indicators |
| `marketshield_prequential_predictions.csv` | Combined replay table with labels and both model probabilities |
| `marketshield_prequential_summary.csv` | Validation and replay scores at frozen, validation-selected thresholds |
| `marketshield_threshold_tradeoff.csv` | Threshold sensitivity: precision, recall, F1, and confusion counts across 29 levels |
| `marketshield_improved_backtest_results.csv` | Expanding-window regression backtest results across 7 calendar years |
| `docs/MODEL_VALIDATION_V2.md` | Detailed experiment report with model comparison |
| `docs/INDEPENDENT_VALIDATION_PLAN.md` | Protocol for external data matching and independent temporal evaluation |
| `docs/independent_external_audit_moit_weekly_prices.csv` | Weekly price observations from Yemen Ministry of Industry and Trade (August–September 2026) |
| `requirements-validation.txt` | LightGBM dependency specification for model retraining |

## Execution Instructions

1. Install required Python packages: `pandas`, `numpy`, `scikit-learn`, `lightgbm`, `matplotlib`, `jupyter`.
2. Place the three World Bank ZIP archives alongside the notebook.
3. To reproduce included metric tables using cached predictions, also place the two model prediction-cache CSV files alongside the notebook. The notebook verifies key/label agreement before comparing model outputs.
4. To refit models at each monthly origin instead of using cached prequential predictions, set `RETRAIN_MODELS = True` in Section 5 of the notebook. This is computationally more expensive.

## Current Status

This is a research prototype. The later-period replay was examined during earlier project development and is not an untouched final holdout. The World Bank series is retrospective and may contain model-estimated values. The warning target is defined as a greater-than-5% change in a close estimate, not a validated humanitarian outcome indicator.
