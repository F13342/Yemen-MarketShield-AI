# Yemen MarketShield AI — Complete Research Submission Package

**Project type:** reproducible research / model-validation package (Jupyter notebooks, source snapshots, generated results and reports).
**Status:** research prototype only. This package is not a production service or an operational food-security early-warning system.

## Project at a glance

Yemen MarketShield AI studies whether monthly wheat-price changes in Yemen can be described or flagged using historical market data. The package contains two related but distinct evaluations:

1. **World Bank retrospective walk-forward replay** — LightGBM classifiers predict whether the next consecutive month’s World Bank `c_wheat` close estimate is more than 5% above the current month. The notebook compares core price/seasonality features with expanded data-quality features and includes a threshold trade-off table.
2. **WFP HAPI actual-price temporal experiment** — a separate experiment based on actual monthly retail wheat observations returned by HDX HAPI. It compares simple baselines and regression models, and evaluates an exploratory >5% rise classifier on April–September 2026.

These experiments should not be conflated: the WFP experiment is a separate target-series experiment, and the matching of WFP and World Bank history is approximate. Potential upstream data overlap means it is **not claimed as fully independent-source validation**.

## Main files

- `Yemen_MarketShield_Model_Validation.ipynb` — primary World Bank temporal validation notebook.
- `Yemen_MarketShield_WFP_External_Validation.ipynb` — WFP HAPI experiment; adapted for both local VS Code/Jupyter and Google Colab.
- `docs/PROJECT_SUMMARY.md` — concise methods, result tables and limitations.
- `docs/MODEL_VALIDATION_V2.md` — detailed World Bank experiment report.
- `docs/MODEL_VALIDATION_REPORT_WFP.md` — detailed WFP temporal experiment report.
- `docs/INDEPENDENT_VALIDATION_PLAN.md` — next steps for truly independent evaluation.
- `marketshield_prequential_core_predictions.csv`, `marketshield_prequential_enhanced_predictions.csv` — cached per-origin probabilities.
- `marketshield_prequential_predictions.csv`, `marketshield_prequential_summary.csv`, `marketshield_threshold_tradeoff.csv` — combined predictions and regenerated metrics.
- `marketshield_improved_backtest_results.csv` — supplementary selected-year regression benchmark.
- `results/` — generated WFP matched-pair, validation/test predictions and metric tables.
- `scripts/validate_submission.py` — lightweight integrity checks for notebooks and output files.

## Quick start on Windows / VS Code

Open this folder in VS Code. Create/select a Python environment (Python 3.10 or later is recommended), then in the integrated terminal run:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/validate_submission.py
```

Open each notebook and choose the same environment as the notebook kernel.

- Run `Yemen_MarketShield_Model_Validation.ipynb` from the first cell to the end. The three dated World Bank ZIP archives and prediction cache CSVs are included beside the notebook. `RETRAIN_MODELS = False` reuses caches only after their keys, labels and source-derived target/baseline values validate. Set it to `True` to refit both models at every forecast origin; this takes longer.
- Run `Yemen_MarketShield_WFP_External_Validation.ipynb` from the first cell to the end. Locally it discovers `WFP_Wheat_Yemen_HAPI_Response.json` and `YEM_RTFP_mkt_2009_2026-03-24.zip` in this folder. In Colab, upload those two files when prompted. WFP results are written to `results/` and bundled as `Yemen_MarketShield_WFP_Validation_Outputs.zip`.

The notebooks are designed to be run top-to-bottom. If a cache is rejected or an output differs, retain the terminal/notebook message and investigate before committing regenerated artifacts.

## Main World Bank result snapshot

The included run produced 2,088 aligned predictions (24 local markets × 87 forecast origins), with 864 validation examples and 1,224 later-period replay examples. The later period was already inspected during earlier development and is therefore **not an untouched holdout**.

| Model / split | Threshold | Precision | Recall | F1 | Alerts | False alerts |
|---|---:|---:|---:|---:|---:|---:|
| Core — validation | 0.475 | 0.435 | 0.670 | 0.528 | 285 | 161 |
| Core — later replay | 0.475 | 0.224 | 0.555 | 0.319 | 384 | 298 |
| Expanded quality — validation | 0.500 | 0.459 | 0.611 | 0.524 | 246 | 133 |
| Expanded quality — later replay | 0.500 | 0.223 | 0.510 | 0.310 | 355 | 276 |

The expanded indicators did not improve overall later-period F1. In the later replay, about 77.6% of core alerts and 77.7% of expanded-quality alerts were false positives. This is not adequate evidence for operational warning use.

## WFP temporal experiment snapshot

- HAPI response: 936 source records, 23 markets; the filtered series covers actual retail wheat prices in YER/kg.
- Historical source comparison: 851 matched market-period pairs (January 2022–March 2026); the month alignment is approximate and may share upstream provenance.
- Future test: 62 market-period rows across 11 markets, April–September 2026.
- The previous-period baseline obtained test MAE 20.00 YER/kg and WAPE 2.41%; Gradient Boosting had lower RMSE but worse MAE/WAPE.
- The exploratory warning classifier had 6 positive events in the test set, precision 9.1%, recall 83.3%, F1 0.164 and ROC-AUC 0.479, with 50 false positives. These estimates are highly uncertain and do not support deployment.

## Reproducibility and data-use notes

- Raw World Bank ZIP archives and the supplied HAPI response are included **in this local academic handoff bundle** so the notebooks can be rerun. Before uploading raw source data to a public GitHub repository, review the source providers' reuse/licensing conditions. The public GitHub link may intentionally carry code, reports and derived artifacts without these raw files.
- Do not commit a private HDX HAPI `app_identifier` or other credentials. No API credential is needed to run this package because the supplied response snapshot is used.
- All scores are retrospective. The WFP future period in this package has already been inspected and cannot be treated as an untouched future test for a new round of model tuning.
- This package does not include a hosted website, live API, database service, alert delivery, calibrated production model or operational monitoring pipeline.

## Public repository

Repository: https://github.com/F13342/Yemen-MarketShield-AI
Validation workbench branch: https://github.com/F13342/Yemen-MarketShield-AI/tree/experiment/validation-workbench
Pull request #2 (still a draft at the time this bundle was prepared): https://github.com/F13342/Yemen-MarketShield-AI/pull/2
