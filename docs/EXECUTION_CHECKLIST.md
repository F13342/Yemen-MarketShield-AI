# Execution and QA Checklist

Prepared on 22 October 2026 for the local academic handoff bundle and public GitHub workbench.

## Notebook executions

- [x] `Yemen_MarketShield_Model_Validation.ipynb` executed top-to-bottom from a fresh kernel in a clean staging folder.
- [x] Main notebook found all three dated World Bank source archives.
- [x] Main notebook validated both cached per-origin prediction tables against source-derived keys, labels, next-month changes and momentum-baseline values.
- [x] Combined prediction table shape: 2,088 rows × 9 columns.
- [x] Main summary regenerated with four model/split rows and 17 columns.
- [x] Threshold trade-off table regenerated with 58 rows; model labels are `core` and `expanded_quality`.
- [x] `Yemen_MarketShield_WFP_External_Validation.ipynb` executed top-to-bottom from a fresh kernel in local mode.
- [x] WFP source response parsed: 936 input records; filtered series covers 23 markets.
- [x] WFP/World Bank historical comparison produced 851 matched pairs.
- [x] WFP temporal test generated 62 regression/classification prediction rows across 11 markets.
- [x] `scripts/validate_submission.py` passed 37 structural, schema, label and metric-consistency checks.

## Public GitHub clone versus local handoff

The public GitHub branch intentionally omits the raw World Bank ZIP archives and raw WFP HAPI JSON snapshot pending source redistribution review. The local academic handoff bundle used for the recorded notebook executions included those files. On a clean clone, `scripts/validate_submission.py` checks tracked notebooks and derived outputs and prints informational notes for missing raw inputs; notebooks cannot be fully rerun until the source snapshots are obtained as described in `README.md` and `README_AR.md`.

## What these checks do not establish

- They do not establish that the model is operationally ready.
- They do not turn the later World Bank replay or the analysed April–September 2026 WFP window into untouched independent holdouts.
- They do not establish independence of World Bank and WFP source provenance.
- Cached probabilities in the World Bank experiment are validated against source-derived row keys and target/baseline values, but cache validation alone is not cryptographic proof of the exact model code/version that originally produced every probability. Set `RETRAIN_MODELS = True` to refit the monthly models from the included source archives.
- Raw-source licensing terms should be checked before any public GitHub upload of the raw archives/response JSON.
