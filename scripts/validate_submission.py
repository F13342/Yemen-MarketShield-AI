#!/usr/bin/env python3
"""Lightweight integrity checks for the Yemen MarketShield research submission."""
from __future__ import annotations

import json
import math
import sys
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
errors: list[str] = []
checks: list[str] = []
notes: list[str] = []


def require(condition: bool, message: str) -> None:
    if condition:
        checks.append(message)
    else:
        errors.append(message)


# Raw source inputs are intentionally excluded from the public repository.
# Validate them when present (for a local handoff bundle), but do not fail a
# clean GitHub clone just because source snapshots were not redistributed.
source_files = [
    "YEM_RTFP_mkt_2009_2026-03-24.zip",
    "YEM_RTFX_mkt_2009_2026-03-24.zip",
    "YEM_RTEP_mkt_2009_2026-03-24.zip",
    "WFP_Wheat_Yemen_HAPI_Response.json",
]
for name in source_files:
    if (ROOT / name).is_file():
        checks.append(f"optional source input present: {name}")
    else:
        notes.append(f"Source input not committed: {name}; obtain it using the README source instructions before re-running notebooks.")
for prefix in ["YEM_RTFP", "YEM_RTFX", "YEM_RTEP"]:
    path = next(iter(ROOT.glob(prefix + "*.zip")), None)
    if path:
        try:
            with zipfile.ZipFile(path) as z:
                csvs = [n for n in z.namelist() if n.lower().endswith(".csv")]
            require(bool(csvs), f"archive contains CSV: {path.name}")
        except zipfile.BadZipFile:
            errors.append(f"archive is invalid ZIP: {path.name}")

# Notebook JSON, cell structure, and pure Python syntax for code cells.
for name in ["Yemen_MarketShield_Model_Validation.ipynb", "Yemen_MarketShield_WFP_External_Validation.ipynb"]:
    path = ROOT / name
    try:
        notebook = json.loads(path.read_text(encoding="utf-8"))
        require(notebook.get("nbformat") == 4 and bool(notebook.get("cells")), f"valid notebook JSON: {name}")
        for i, cell in enumerate(notebook.get("cells", []), start=1):
            if cell.get("cell_type") != "code":
                continue
            source = cell.get("source", "")
            source = "".join(source) if isinstance(source, list) else source
            try:
                compile(source, f"{name}:cell{i}", "exec")
            except SyntaxError as exc:
                errors.append(f"syntax error in {name} cell {i}: {exc}")
        if not any(e.startswith(f"syntax error in {name}") for e in errors):
            checks.append(f"Python syntax checked: {name}")
    except Exception as exc:
        errors.append(f"cannot read notebook {name}: {exc}")

# World Bank outputs.
try:
    core = pd.read_csv(ROOT / "marketshield_prequential_core_predictions.csv", parse_dates=["price_date", "next_date"])
    enhanced = pd.read_csv(ROOT / "marketshield_prequential_enhanced_predictions.csv", parse_dates=["price_date", "next_date"])
    combined = pd.read_csv(ROOT / "marketshield_prequential_predictions.csv", parse_dates=["price_date", "next_date"])
    summary = pd.read_csv(ROOT / "marketshield_prequential_summary.csv")
    tradeoff = pd.read_csv(ROOT / "marketshield_threshold_tradeoff.csv")

    keys = ["geo_id", "price_date", "next_date"]
    require(len(core) == 2088 and not core.duplicated(keys).any(), "core prediction cache has 2,088 unique market/origin keys")
    require(len(enhanced) == 2088 and not enhanced.duplicated(keys).any(), "expanded prediction cache has 2,088 unique market/origin keys")
    require(len(combined) == 2088 and not combined.duplicated(keys).any(), "combined predictions have 2,088 unique keys")
    require(list(summary.columns) == ["model", "split", "threshold", "n", "positive_rate", "roc_auc", "average_precision", "precision", "recall", "f1", "balanced_accuracy", "alerts", "TP", "FP", "FN", "TN", "false_alert_share"], "World Bank summary retains 17 expected columns")
    require(len(summary) == 4, "World Bank summary has four model/split rows")
    require(set(summary["model"].astype(str)) == {"core", "expanded_quality"}, "stable model labels used in summary")
    require(set(summary["split"].astype(str)) == {"validation", "later_period_replay"}, "expected validation/replay split labels")
    require(len(tradeoff) == 58 and set(tradeoff["model"].astype(str)) == {"core", "expanded_quality"}, "threshold trade-off has 58 rows and stable model labels")
    for _, row in summary.iterrows():
        tp, fp, fn = int(row["TP"]), int(row["FP"]), int(row["FN"])
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        require(math.isclose(precision, float(row["precision"]), rel_tol=2e-5, abs_tol=1e-6), f"precision reconciles with confusion counts: {row['model']} / {row['split']}")
        require(math.isclose(recall, float(row["recall"]), rel_tol=2e-5, abs_tol=1e-6), f"recall reconciles with confusion counts: {row['model']} / {row['split']}")
        require(math.isclose(f1, float(row["f1"]), rel_tol=2e-5, abs_tol=1e-6), f"F1 reconciles with confusion counts: {row['model']} / {row['split']}")
except Exception as exc:
    errors.append(f"World Bank result validation failed: {exc}")

# WFP outputs from the executed notebook.
try:
    historical = pd.read_csv(ROOT / "results" / "wfp_worldbank_historical_pairs.csv")
    reg_val = pd.read_csv(ROOT / "results" / "wfp_regression_validation_metrics.csv")
    reg_test = pd.read_csv(ROOT / "results" / "wfp_regression_future_test_metrics.csv")
    reg_pred = pd.read_csv(ROOT / "results" / "wfp_regression_future_test_predictions.csv")
    class_val = pd.read_csv(ROOT / "results" / "wfp_classifier_validation_thresholds.csv")
    class_test = pd.read_csv(ROOT / "results" / "wfp_classifier_future_test_metrics.csv")
    class_pred = pd.read_csv(ROOT / "results" / "wfp_classifier_future_test_predictions.csv")
    require(len(historical) == 851 and historical["market_name"].nunique() == 23, "WFP/World Bank historical table has 851 pairs across 23 markets")
    require(len(reg_val) == 6, "WFP regression validation table has six benchmark rows")
    require(len(reg_test) == 4 and len(reg_pred) == 62, "WFP regression test has four models and 62 predictions")
    require(len(class_val) == 91, "WFP classifier threshold scan has 91 validation thresholds")
    require(len(class_test) == 1 and int(class_test.loc[0, "rows"]) == 62, "WFP classifier test metrics describe 62 rows")
    require(len(class_pred) == 62, "WFP classifier has 62 row-level test predictions")
except Exception as exc:
    errors.append(f"WFP result validation failed: {exc}")

print("Yemen MarketShield AI — submission integrity check")
print(f"Root: {ROOT}")
print(f"Passed checks: {len(checks)}")
for item in checks:
    print("  PASS:", item)
for item in notes:
    print("  INFO:", item)
if errors:
    print(f"FAILED checks: {len(errors)}")
    for item in errors:
        print("  FAIL:", item)
    sys.exit(1)
print("RESULT: PASS — artifact integrity checks succeeded.")
print("Note: this is not evidence of operational or independent scientific validation.")
