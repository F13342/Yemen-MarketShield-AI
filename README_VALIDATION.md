# Yemen MarketShield AI — Validation Workbench

This folder is a separate research/validation workbench. **It has not been pushed to the public GitHub repository.** It contains the walk-forward notebook, summary outputs, prediction-cache files, and the plan for an independent external evaluation.

## Files

- `Yemen_MarketShield_Model_Validation.ipynb`: source-data merge, feature construction, monthly walk-forward methodology, threshold selection, and comparison of core vs expanded LightGBM.
- `marketshield_prequential_core_predictions.csv`: per-market, per-origin predictions from the 73-feature core model.
- `marketshield_prequential_enhanced_predictions.csv`: predictions from the 101-feature model with data-quality features.
- `marketshield_prequential_predictions.csv`: aligned combined replay table, with labels and both model probabilities.
- `marketshield_prequential_summary.csv`: validation/replay scores from the frozen validation-selected thresholds.
- `marketshield_threshold_tradeoff.csv`: validation threshold vs precision/recall/F1 and confusion counts.
- `marketshield_improved_backtest_results.csv`: supplementary regression backtest results.
- `docs/MODEL_VALIDATION_V2.md`: report with latest comparison.
- `docs/INDEPENDENT_VALIDATION_PLAN.md`: plan for external data matching and truly independent temporal evaluation.
- `docs/independent_external_audit_moit_weekly_prices.csv`: five weekly observations published by Yemen's Ministry of Industry, Trade and Investment for Aug 20–Sep 17, 2026; this is a discovery/audit aid, not a scored test of the current model.
- `requirements-validation.txt`: LightGBM dependency for full retraining.

## Running

1. Install Python packages (`pandas`, `numpy`, `scikit-learn`, `lightgbm`, `jupyter`).
2. Put the three World Bank ZIP archives next to the notebook, or use Colab's upload dialog.
3. To reproduce the included metric tables quickly, also place/upload the two model prediction-cache CSVs next to the notebook. The notebook checks key/label agreement before comparing model outputs.
4. To refit models at each monthly origin instead of using the cached prequential predictions, set `RETRAIN_MODELS = True` in section 5. This is computationally more expensive.

## Current decision

Research prototype only. The later-period replay was already inspected during earlier project development and is not an untouched final holdout. The World Bank series is retrospective and may contain model-estimated values. The current warning target is a >5% change in a close estimate, not a validated humanitarian outcome. Do not use it for operational warning decisions.

No raw World Bank ZIPs are included in this package; download them from the official source links in the notebook/report and review any redistribution terms before committing derived data publicly.
