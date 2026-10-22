# Yemen MarketShield AI

## Wheat-price monitoring and risk analytics for Yemen

**Product status:** research and decision-support prototype. The current release provides reproducible data analysis, retrospective risk scoring, forecast evaluation and audit-oriented reports. It is not a live alerting service and has not been validated for operational humanitarian, procurement, financial or public-warning decisions.

## Product overview

Yemen MarketShield AI explores whether historical market prices and time-aware signals can help identify months in which recorded wheat-price estimates may rise sharply. It combines data-quality checks, chronological model evaluation, baseline comparisons, threshold sensitivity, market-level summaries and anomaly exploration in a single version-controlled workbench.

The primary outcome is defined as a greater-than-5% increase in the World Bank `c_wheat` monthly close estimate at the next consecutive month. This is a project-specific statistical target; it is not an official food-insecurity, food-crisis or humanitarian-needs indicator.

## Core components

| Component | Purpose |
|---|---|
| `Yemen_MarketShield_Initial_Analysis.ipynb` | Data exploration, source consistency checks and initial forecasting baselines |
| `Yemen_MarketShield_Model_Validation.ipynb` | Monthly walk-forward replay, cache validation, threshold selection and LightGBM evaluation |
| `Yemen_MarketShield_WFP_External_Validation.ipynb` | Separate analysis of actual retail wheat prices returned through HDX HAPI |
| `scripts/analyze_marketshield.py` | Generates product analytics, temporal model comparisons, PCA diagnostics and anomaly summaries without target-derived features |
| `scripts/validate_submission.py` | Checks notebook integrity, output schemas, key uniqueness and metric consistency |
| `docs/PROJECT_SUMMARY.md` | Methods, metrics and interpretation in one place |
| `docs/PROJECT_REPORT.md` | Description of the initial experiments and their limitations |
| `docs/MODEL_VALIDATION_V2.md` | Detailed temporal evaluation of the World Bank experiment |
| `docs/MODEL_VALIDATION_REPORT_WFP.md` | Results of the separate WFP/HAPI experiment |
| `docs/DATA_SOURCES.md` | Data provenance, joins, units and interpretation notes |
| `docs/INDEPENDENT_VALIDATION_PLAN.md` | Protocol for obtaining and evaluating an independent test source |
| `results/product_analysis/` | Generated analytical figures and machine-readable outputs |
| `results/` | WFP experiment result tables and predictions |

## Method and current evidence

### World Bank monthly replay

The current prediction artifact contains 2,088 market-origin rows across 24 local markets: 864 rows in the 2019–2021 validation window and 1,224 rows in the later replay window beginning in 2022. Thresholds were selected on the validation window and kept fixed for the later replay.

| Model / split | Threshold | ROC-AUC | Precision | Recall | F1 | Alerts | False alerts |
|---|---:|---:|---:|---:|---:|---:|---:|
| LightGBM core — validation | 0.475 | 0.749 | 0.435 | 0.670 | 0.528 | 285 | 161 |
| LightGBM core — later replay | 0.475 | 0.684 | 0.224 | 0.555 | 0.319 | 384 | 298 |
| Expanded quality — validation | 0.500 | 0.747 | 0.459 | 0.611 | 0.524 | 246 | 133 |
| Expanded quality — later replay | 0.500 | 0.680 | 0.223 | 0.510 | 0.310 | 355 | 276 |

The later replay shows a high false-alert burden, around 77.6% for the core model and 77.7% for the expanded model. Additional quality indicators did not improve later-replay F1 in the current run.

### WFP/HDX HAPI experiment

The separate HAPI analysis contains 62 later-period rows across 11 markets for April–September 2026. The previous-period regression baseline achieved MAE of about 20 YER/kg and WAPE of about 2.41%. The exploratory greater-than-5% rise classifier produced 55 alerts, including 50 false positives, and F1 of about 0.164. These results do not support operational alerting.

## Reproducibility

### Environment setup (Windows / VS Code)

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -r requirements-validation.txt
python .\scripts\validate_submission.py
python .\scripts\analyze_marketshield.py
```

Open notebooks in VS Code or Jupyter and select the same Python environment. Run notebook cells from top to bottom.

### Source inputs

Raw source snapshots are intentionally excluded from the public repository until redistribution terms are confirmed. To rerun the main notebooks, obtain the World Bank release dated `2026-03-24` from the source catalogues and place the three ZIP archives next to the notebooks:

- Food prices: https://microdata.worldbank.org/catalog/4508
- Exchange rates: https://microdata.worldbank.org/catalog/6159
- Energy prices: https://microdata.worldbank.org/catalog/6133

The WFP/HAPI notebook additionally needs a saved response snapshot for Yemen wheat retail prices in YER/kg. Use the HDX HAPI usage guide: https://hdx-hapi.readthedocs.io/en/latest/data_usage_guides/food_security_nutrition_and_poverty/. Do not add API credentials, app identifiers or other secrets to the repository. The committed `results/` files are derived outputs; the result archive does not contain the raw HAPI input.

The supplementary analysis script uses only predictors known at the forecast origin (`previous_month_change`, calendar features and market ID). It excludes `next_pct_change` and `shock_gt5` from the model feature matrix. Learning-history and regularization settings are assessed on a chronological internal validation window; the later replay is not used to choose hyperparameters.

## Limitations and intended use

1. The later World Bank replay was examined during earlier development and is not an untouched independent holdout.
2. The World Bank series contains monthly close estimates and can be revised; a frozen historical file does not prove that each value was available in exactly that form at every historical forecast origin.
3. Historical agreement between World Bank and HAPI data is descriptive. The sources may share upstream provenance, and their measurement periods or product definitions may differ.
4. The HAPI later-period window has already been examined and must not be treated as an untouched final test for further model selection.
5. The high false-alert rate indicates that the current models are not suitable for operational alerts without further independent testing, calibration, user-centered cost analysis and silent evaluation.
6. The current repository is a research/decision-support prototype. It does not include a hosted dashboard, live API, alert-delivery service or production monitoring pipeline.

## Project links

- Repository: https://github.com/F13342/Yemen-MarketShield-AI
- Validation branch: https://github.com/F13342/Yemen-MarketShield-AI/tree/experiment/validation-workbench
- Review request: https://github.com/F13342/Yemen-MarketShield-AI/pull/2
