# Execution and Quality Assurance Checklist

**Purpose:** document integrity and reproducibility checks for the Yemen MarketShield AI product prototype.

## Verified artifacts

- [x] `Yemen_MarketShield_Model_Validation.ipynb` executed top-to-bottom from a fresh kernel in a clean staging directory.
- [x] The dated World Bank source archives were loaded successfully in the local handoff environment.
- [x] Cached per-origin prediction tables were checked against source-derived keys, labels, next-month changes and baseline values.
- [x] Combined World Bank prediction artifact contains 2,088 rows and 9 columns.
- [x] World Bank summary contains four model/split rows and 17 columns.
- [x] Threshold sensitivity output contains 58 rows using the stable labels `core` and `expanded_quality`.
- [x] `Yemen_MarketShield_WFP_External_Validation.ipynb` executed top-to-bottom in the local handoff environment.
- [x] WFP source response parsed: 936 input records; filtered series covers 23 markets.
- [x] Historical HAPI/World Bank matching produced 851 market-period pairs.
- [x] WFP later-period analysis contains 62 regression/classification prediction rows across 11 markets.
- [x] `scripts/validate_submission.py` checks notebook structure, cached result schemas, key uniqueness and metric consistency.
- [x] `scripts/analyze_marketshield.py` generates product analytics from existing prediction artifacts.

## Public-repository and local-handoff distinction

Raw World Bank ZIP archives and the raw WFP HAPI JSON snapshot are ignored by Git until redistribution terms have been reviewed. They are included in the local project bundle for reproducibility. A clean public clone can run integrity checks on committed notebooks and derived outputs, but full notebook reruns require obtaining the raw source inputs as described in `README.md` and `README_AR.md`.

## Interpretation limits

These checks establish structural integrity and consistency of selected metrics; they do not establish:

- operational readiness of the models;
- an untouched independent holdout for the World Bank later replay or the WFP April–September 2026 window;
- independence of World Bank and HAPI source provenance;
- that historical estimated values were available in exactly the same form at each historical forecast origin;
- suitability for humanitarian allocation, procurement, finance or public warnings.

The current release is a research and decision-support prototype, not a live monitoring/alert delivery service.
