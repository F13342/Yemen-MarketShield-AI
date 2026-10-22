#!/usr/bin/env python3
"""Yemen MarketShield AI — product analytics and retrospective evaluation.

This script generates descriptive analytics from the saved walk-forward predictions.
It deliberately does not use future target-derived columns as features and does not
select hyperparameters on the later replay window. That window has already been
examined during development and is not an untouched independent holdout.
"""
from __future__ import annotations

import json
import warnings
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.decomposition import PCA
from sklearn.ensemble import (
    GradientBoostingClassifier,
    IsolationForest,
    RandomForestClassifier,
)
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    balanced_accuracy_score,
    confusion_matrix,
    f1_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.tree import DecisionTreeClassifier, export_text

warnings.filterwarnings("default", category=UserWarning)
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results" / "product_analysis"
OUT.mkdir(parents=True, exist_ok=True)
RANDOM_STATE = 42
VALIDATION_END = pd.Timestamp("2021-12-31")
REPLAY_START = pd.Timestamp("2022-01-01")
INTERNAL_VALIDATION_START = pd.Timestamp("2021-07-01")

plt.rcParams.update({
    "figure.dpi": 150,
    "savefig.dpi": 160,
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.labelsize": 10,
    "figure.facecolor": "white",
})


def require_columns(frame: pd.DataFrame, columns: list[str], file_name: str) -> None:
    missing = sorted(set(columns) - set(frame.columns))
    if missing:
        raise ValueError(f"{file_name} is missing required columns: {missing}")


def make_preprocessor() -> ColumnTransformer:
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])
    market_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC_FEATURES),
        ("market", market_pipe, [MARKET_FEATURE]),
    ], remainder="drop", verbose_feature_names_out=False)


def make_pipeline(estimator) -> Pipeline:
    return Pipeline([
        ("preprocess", make_preprocessor()),
        ("model", estimator),
    ])


def positive_score(estimator: Pipeline, X: pd.DataFrame) -> np.ndarray:
    model = estimator.named_steps["model"]
    if hasattr(model, "predict_proba"):
        return estimator.predict_proba(X)[:, 1]
    decision = estimator.decision_function(X)
    # Scores are used only for ranking metrics; model.predict keeps its standard decision rule.
    return np.asarray(decision, dtype=float)


def classification_metrics(y_true, y_pred, score, model: str, split: str, threshold=None) -> dict:
    tn, fp, fn, tp = confusion_matrix(y_true, y_pred, labels=[0, 1]).ravel()
    row = {
        "model": model,
        "split": split,
        "n": int(len(y_true)),
        "positive_rate": float(np.mean(y_true)) if len(y_true) else float("nan"),
        "precision": float(precision_score(y_true, y_pred, zero_division=0)),
        "recall": float(recall_score(y_true, y_pred, zero_division=0)),
        "f1": float(f1_score(y_true, y_pred, zero_division=0)),
        "balanced_accuracy": float(balanced_accuracy_score(y_true, y_pred)),
        "alerts": int(np.sum(y_pred)),
        "TP": int(tp), "FP": int(fp), "FN": int(fn), "TN": int(tn),
        "false_alert_share": float(fp / (tp + fp)) if tp + fp else 0.0,
        "threshold_or_rule": threshold,
    }
    if len(np.unique(y_true)) > 1:
        row["roc_auc"] = float(roc_auc_score(y_true, score))
        row["average_precision"] = float(average_precision_score(y_true, score))
    else:
        row["roc_auc"] = float("nan")
        row["average_precision"] = float("nan")
    return row


def savefig(fig, filename: str) -> None:
    fig.tight_layout()
    fig.savefig(OUT / filename, bbox_inches="tight")
    plt.close(fig)


print("=" * 74)
print("Yemen MarketShield AI — Product Analytics")
print("=" * 74)

prediction_path = ROOT / "marketshield_prequential_predictions.csv"
summary_path = ROOT / "marketshield_prequential_summary.csv"
threshold_path = ROOT / "marketshield_threshold_tradeoff.csv"
backtest_path = ROOT / "marketshield_improved_backtest_results.csv"
for p in [prediction_path, summary_path, threshold_path, backtest_path]:
    if not p.is_file():
        raise FileNotFoundError(f"Required artifact not found: {p.name}")

pred = pd.read_csv(prediction_path)
require_columns(pred, [
    "geo_id", "price_date", "next_date", "mkt_name", "shock_gt5",
    "next_pct_change", "previous_month_change", "prob_core", "prob_enhanced",
], prediction_path.name)
pred["price_date"] = pd.to_datetime(pred["price_date"], errors="raise")
pred["next_date"] = pd.to_datetime(pred["next_date"], errors="raise")
pred["shock_gt5"] = pd.to_numeric(pred["shock_gt5"], errors="raise").astype(int)
if not set(pred["shock_gt5"].unique()).issubset({0, 1}):
    raise ValueError("shock_gt5 must be binary (0/1).")
if pred.duplicated(["geo_id", "price_date", "next_date"]).any():
    raise ValueError("Duplicate market/origin rows found in the prediction artifact.")

# Only predictors known at the current forecast origin are used for newly fitted analyses.
# next_pct_change and shock_gt5 are outcomes and must never be included in model features.
NUMERIC_FEATURES = ["previous_month_change", "month_sin", "month_cos", "year_index"]
MARKET_FEATURE = "mkt_name"
pred["origin_month"] = pred["price_date"].dt.month
pred["month_sin"] = np.sin(2 * np.pi * pred["origin_month"] / 12)
pred["month_cos"] = np.cos(2 * np.pi * pred["origin_month"] / 12)
pred["year_index"] = pred["price_date"].dt.year - int(pred["price_date"].dt.year.min())
pred["previous_month_change"] = pd.to_numeric(pred["previous_month_change"], errors="coerce")

# Main score reports retain the existing validation/replay split and frozen thresholds.
validation = pred.loc[pred["next_date"] <= VALIDATION_END].copy()
replay = pred.loc[pred["next_date"] >= REPLAY_START].copy()
if validation.empty or replay.empty:
    raise ValueError("Expected non-empty validation (through 2021) and later replay (2022 onward) windows.")

summary_rows = []
for split_name, frame in [("validation", validation), ("later_period_replay_retrospective", replay)]:
    y = frame["shock_gt5"].to_numpy()
    for label, col, threshold in [
        ("LightGBM core", "prob_core", 0.475),
        ("LightGBM expanded quality", "prob_enhanced", 0.500),
    ]:
        score = pd.to_numeric(frame[col], errors="coerce").to_numpy(dtype=float)
        pred_label = (score >= threshold).astype(int)
        summary_rows.append(classification_metrics(y, pred_label, score, label, split_name, threshold))
    # Momentum baseline uses only the previous-month percentage change, available at origin.
    momentum = (frame["previous_month_change"].fillna(-np.inf).to_numpy() > 0.05).astype(int)
    summary_rows.append(classification_metrics(y, momentum, momentum.astype(float), "Momentum baseline", split_name, "previous_month_change > 0.05"))
summary_df = pd.DataFrame(summary_rows)
summary_df.to_csv(OUT / "primary_model_metrics.csv", index=False, lineterminator="\n")
print(f"Rows: {len(pred)} | Validation: {len(validation)} | Later replay: {len(replay)}")

# 1) ROC and precision-recall curves for existing out-of-origin model scores.
fig, axes = plt.subplots(1, 2, figsize=(13, 5.4))
for frame, split_name, line_style in [(validation, "Validation 2019–2021", "-"), (replay, "Later replay 2022+ (retrospective)", ":")]:
    y = frame["shock_gt5"].to_numpy()
    if len(np.unique(y)) < 2:
        continue
    for label, col, color in [
        ("Core", "prob_core", "#2563eb"),
        ("Expanded quality", "prob_enhanced", "#dc2626"),
    ]:
        score = frame[col].to_numpy(dtype=float)
        fpr, tpr, _ = roc_curve(y, score)
        axes[0].plot(fpr, tpr, linestyle=line_style, color=color, linewidth=2,
                     label=f"{label} — {split_name} (AUC {roc_auc_score(y, score):.3f})")
        precision, recall, _ = precision_recall_curve(y, score)
        axes[1].plot(recall, precision, linestyle=line_style, color=color, linewidth=2,
                     label=f"{label} — {split_name} (AP {average_precision_score(y, score):.3f})")
axes[0].plot([0, 1], [0, 1], "k--", alpha=0.35)
axes[0].set(title="Classification ranking quality", xlabel="False-positive rate", ylabel="True-positive rate")
axes[1].set(title="Precision–recall performance", xlabel="Recall", ylabel="Precision")
for ax in axes:
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7, loc="best")
savefig(fig, "classification_performance_curves.png")

# 2) Threshold sensitivity is calculated from validation-only rows; no replay tuning.
thresholds = pd.read_csv(threshold_path)
require_columns(thresholds, ["model", "validation_threshold", "precision", "recall", "f1"], threshold_path.name)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for ax, model_name in zip(axes, ["core", "expanded_quality"]):
    subset = thresholds.loc[thresholds["model"].astype(str).eq(model_name)].sort_values("validation_threshold")
    if subset.empty:
        ax.set_visible(False)
        continue
    ax.plot(subset["validation_threshold"], subset["precision"], "o-", ms=3, label="Precision")
    ax.plot(subset["validation_threshold"], subset["recall"], "s-", ms=3, label="Recall")
    ax.plot(subset["validation_threshold"], subset["f1"], "^-", ms=3, label="F1")
    best = subset.loc[subset["f1"].idxmax()]
    ax.axvline(float(best["validation_threshold"]), color="#15803d", linestyle="--", alpha=0.65,
               label=f"Best validation F1 threshold: {best['validation_threshold']:.3f}")
    ax.set(title=f"Validation threshold sensitivity — {model_name.replace('_', ' ')}",
           xlabel="Probability threshold", ylabel="Score", ylim=(0, 1))
    ax.grid(alpha=0.25)
    ax.legend(fontsize=8)
savefig(fig, "validation_threshold_sensitivity.png")

# 3) Train auxiliary models on 2019–2021 validation-target rows; score once on later replay.
# This comparison is explicitly retrospective; it is not presented as a clean holdout.
X_train = validation[NUMERIC_FEATURES + [MARKET_FEATURE]].copy()
y_train = validation["shock_gt5"].to_numpy()
X_replay = replay[NUMERIC_FEATURES + [MARKET_FEATURE]].copy()
y_replay = replay["shock_gt5"].to_numpy()
model_factories = {
    "Logistic regression": lambda: LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE),
    "Linear SVM": lambda: LinearSVC(C=1.0, class_weight="balanced", max_iter=10000, random_state=RANDOM_STATE),
    "RBF SVM": lambda: SVC(C=1.0, kernel="rbf", class_weight="balanced", probability=True, random_state=RANDOM_STATE),
    "Decision tree": lambda: DecisionTreeClassifier(max_depth=4, min_samples_leaf=20, class_weight="balanced", random_state=RANDOM_STATE),
    "Random forest": lambda: RandomForestClassifier(n_estimators=250, min_samples_leaf=5, class_weight="balanced", random_state=RANDOM_STATE, n_jobs=-1),
    "Gradient boosting": lambda: GradientBoostingClassifier(n_estimators=100, max_depth=2, learning_rate=0.05, random_state=RANDOM_STATE),
}
comparison_rows = []
fitted_models: dict[str, Pipeline] = {}
for model_name, factory in model_factories.items():
    pipeline = make_pipeline(factory())
    pipeline.fit(X_train, y_train)
    y_hat = pipeline.predict(X_replay).astype(int)
    score = positive_score(pipeline, X_replay)
    comparison_rows.append(classification_metrics(y_replay, y_hat, score, model_name, "later_period_replay_retrospective", "estimator default"))
    fitted_models[model_name] = pipeline

# Add existing temporal model predictions and the momentum rule to the comparison table.
for _, row in summary_df.loc[summary_df["split"].eq("later_period_replay_retrospective")].iterrows():
    comparison_rows.append(row.to_dict())
comparison = pd.DataFrame(comparison_rows).sort_values("model").reset_index(drop=True)
comparison.to_csv(OUT / "retrospective_model_comparison.csv", index=False, lineterminator="\n")

show = comparison.sort_values("f1", ascending=True)
fig, ax = plt.subplots(figsize=(10, 6.4))
colors = ["#64748b" if "LightGBM" not in name else "#2563eb" for name in show["model"]]
bars = ax.barh(show["model"], show["f1"], color=colors)
for bar, value in zip(bars, show["f1"]):
    ax.text(value + 0.004, bar.get_y() + bar.get_height()/2, f"{value:.3f}", va="center", fontsize=8)
ax.set_xlim(0, max(0.4, float(show["f1"].max()) * 1.18))
ax.set_xlabel("F1 at default/frozen decision rule")
ax.set_title("Retrospective replay comparison — not an independent holdout")
ax.grid(axis="x", alpha=0.25)
savefig(fig, "retrospective_model_comparison.png")

# 4) Learning-history sensitivity: expanding past-only history, validation is the final 6 months of 2021.
inner_train = validation.loc[validation["next_date"] < INTERNAL_VALIDATION_START].copy()
inner_val = validation.loc[validation["next_date"] >= INTERNAL_VALIDATION_START].copy()
learning_rows = []
if not inner_train.empty and not inner_val.empty and inner_val["shock_gt5"].nunique() > 1:
    month_values = np.array(sorted(inner_train["next_date"].dropna().unique()))
    for fraction in [0.25, 0.50, 0.75, 1.00]:
        n_months = max(1, int(np.ceil(len(month_values) * fraction)))
        selected_months = set(month_values[:n_months])
        sub = inner_train.loc[inner_train["next_date"].isin(selected_months)]
        if sub["shock_gt5"].nunique() < 2:
            continue
        model = make_pipeline(GradientBoostingClassifier(n_estimators=100, max_depth=2, learning_rate=0.05, random_state=RANDOM_STATE))
        model.fit(sub[NUMERIC_FEATURES + [MARKET_FEATURE]], sub["shock_gt5"].to_numpy())
        pred_inner = model.predict(inner_val[NUMERIC_FEATURES + [MARKET_FEATURE]])
        learning_rows.append({
            "history_fraction": fraction,
            "training_months": int(n_months),
            "training_rows": int(len(sub)),
            "validation_rows": int(len(inner_val)),
            "validation_f1": float(f1_score(inner_val["shock_gt5"], pred_inner, zero_division=0)),
            "validation_precision": float(precision_score(inner_val["shock_gt5"], pred_inner, zero_division=0)),
            "validation_recall": float(recall_score(inner_val["shock_gt5"], pred_inner, zero_division=0)),
        })
learning_df = pd.DataFrame(learning_rows)
learning_df.to_csv(OUT / "expanding_history_sensitivity.csv", index=False, lineterminator="\n")
if not learning_df.empty:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.plot(learning_df["training_rows"], learning_df["validation_f1"], "o-", color="#2563eb", label="F1")
    ax.plot(learning_df["training_rows"], learning_df["validation_precision"], "s--", color="#d97706", label="Precision")
    ax.plot(learning_df["training_rows"], learning_df["validation_recall"], "^--", color="#15803d", label="Recall")
    ax.set(title="Expanding-history sensitivity (time-ordered validation)", xlabel="Training rows", ylabel="Score", ylim=(0, 1))
    ax.legend()
    ax.grid(alpha=0.25)
    savefig(fig, "expanding_history_sensitivity.png")

# 5) Regularization sensitivity: choose C only on the internal 2021 validation window.
regularization_rows = []
if not inner_train.empty and not inner_val.empty and inner_train["shock_gt5"].nunique() > 1 and inner_val["shock_gt5"].nunique() > 1:
    for c_value in [0.01, 0.1, 1.0, 10.0, 100.0]:
        model = make_pipeline(LogisticRegression(C=c_value, class_weight="balanced", max_iter=2000, random_state=RANDOM_STATE))
        model.fit(inner_train[NUMERIC_FEATURES + [MARKET_FEATURE]], inner_train["shock_gt5"].to_numpy())
        val_pred = model.predict(inner_val[NUMERIC_FEATURES + [MARKET_FEATURE]])
        val_score = model.predict_proba(inner_val[NUMERIC_FEATURES + [MARKET_FEATURE]])[:, 1]
        regularization_rows.append({
            "C_inverse_regularization": c_value,
            "validation_f1": float(f1_score(inner_val["shock_gt5"], val_pred, zero_division=0)),
            "validation_precision": float(precision_score(inner_val["shock_gt5"], val_pred, zero_division=0)),
            "validation_recall": float(recall_score(inner_val["shock_gt5"], val_pred, zero_division=0)),
            "validation_roc_auc": float(roc_auc_score(inner_val["shock_gt5"], val_score)),
        })
regularization_df = pd.DataFrame(regularization_rows)
regularization_df.to_csv(OUT / "regularization_sensitivity.csv", index=False, lineterminator="\n")
if not regularization_df.empty:
    fig, ax = plt.subplots(figsize=(8, 4.8))
    for metric in ["validation_f1", "validation_precision", "validation_recall"]:
        ax.plot(regularization_df["C_inverse_regularization"], regularization_df[metric], "o-", label=metric.replace("validation_", "").title())
    ax.set_xscale("log")
    ax.set(title="Regularization sensitivity — internal temporal validation only", xlabel="C (inverse regularization strength)", ylabel="Score", ylim=(0, 1))
    ax.legend()
    ax.grid(alpha=0.25)
    savefig(fig, "regularization_sensitivity.png")

# 6) Feature importance from a tree fitted only to pre-replay rows.
importance_model = fitted_models["Random forest"].named_steps["model"]
preprocessor = fitted_models["Random forest"].named_steps["preprocess"]
feature_names = preprocessor.get_feature_names_out()
importance = pd.DataFrame({"feature": feature_names, "importance": importance_model.feature_importances_}).sort_values("importance", ascending=False)
importance.to_csv(OUT / "feature_importance.csv", index=False, lineterminator="\n")
fig, ax = plt.subplots(figsize=(9, 6))
top_imp = importance.head(15).sort_values("importance")
ax.barh(top_imp["feature"], top_imp["importance"], color="#0f766e")
ax.set(title="Random Forest feature importance", xlabel="Impurity-based importance", ylabel="Input feature")
ax.grid(axis="x", alpha=0.25)
savefig(fig, "feature_importance.png")

# Export an interpretable decision tree description without using later replay labels to fit.
tree_model = fitted_models["Decision tree"].named_steps["model"]
tree_text = export_text(tree_model, feature_names=list(feature_names), max_depth=4)
(OUT / "decision_tree_rules.txt").write_text(
    "Decision tree fitted on target months through 2021-12.\n"
    "Later replay data were not used to fit this tree; the replay window is retrospective, not independent.\n\n"
    + tree_text, encoding="utf-8"
)

# 7) PCA: fit preprocessing and decomposition only on pre-replay rows; target is never an input feature.
X_train_processed = preprocessor.transform(X_train)
X_replay_processed = preprocessor.transform(X_replay)
pca_scaler = StandardScaler()
X_train_scaled = pca_scaler.fit_transform(X_train_processed)
X_replay_scaled = pca_scaler.transform(X_replay_processed)
pca = PCA()
pca.fit(X_train_scaled)
explained = pca.explained_variance_ratio_
cumulative = np.cumsum(explained)
number_95 = int(np.searchsorted(cumulative, 0.95) + 1)
components = PCA(n_components=2)
components.fit(X_train_scaled)
train_pc = components.transform(X_train_scaled)
replay_pc = components.transform(X_replay_scaled)
loadings = pd.DataFrame(components.components_.T, columns=["PC1", "PC2"], index=feature_names)
loadings.index.name = "feature"
loadings.to_csv(OUT / "pca_loadings.csv", lineterminator="\n")
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
axes[0].bar(np.arange(1, len(explained)+1), explained, alpha=0.75, color="#2563eb", label="Per component")
axes[0].plot(np.arange(1, len(cumulative)+1), cumulative, "o-", color="#dc2626", label="Cumulative")
axes[0].axhline(0.95, color="#15803d", linestyle="--", alpha=0.7)
axes[0].set(title="PCA variance captured (fit on pre-replay data)", xlabel="Principal component", ylabel="Explained variance ratio")
axes[0].legend(fontsize=8)
axes[0].grid(alpha=0.25)
normal = replay["shock_gt5"].to_numpy() == 0
axes[1].scatter(replay_pc[normal, 0], replay_pc[normal, 1], s=14, alpha=0.35, label="No >5% rise", color="#2563eb")
axes[1].scatter(replay_pc[~normal, 0], replay_pc[~normal, 1], s=18, alpha=0.65, label=">5% rise", color="#dc2626")
axes[1].set(title="Replay observations projected into training-fitted PCA space", xlabel=f"PC1 ({components.explained_variance_ratio_[0]*100:.1f}%)", ylabel=f"PC2 ({components.explained_variance_ratio_[1]*100:.1f}%)")
axes[1].legend(fontsize=8)
axes[1].grid(alpha=0.25)
savefig(fig, "pca_projection.png")

# 8) Anomaly detection: fit only on the pre-replay feature matrix.
anomaly_detector = IsolationForest(n_estimators=250, contamination=0.10, random_state=RANDOM_STATE, n_jobs=-1)
anomaly_detector.fit(X_train_scaled)
anomaly_label = anomaly_detector.predict(X_replay_scaled)
anomaly_score = anomaly_detector.decision_function(X_replay_scaled)
anomaly_out = replay[["geo_id", "mkt_name", "price_date", "next_date", "shock_gt5"]].copy()
anomaly_out["anomaly_label"] = np.where(anomaly_label == -1, "anomaly", "typical")
anomaly_out["anomaly_score"] = anomaly_score
anomaly_out.to_csv(OUT / "replay_anomaly_scores.csv", index=False, lineterminator="\n")
anomaly_summary = anomaly_out.groupby(["mkt_name", "anomaly_label"], dropna=False).agg(rows=("shock_gt5", "size"), observed_rise_rate=("shock_gt5", "mean"), median_anomaly_score=("anomaly_score", "median")).reset_index()
anomaly_summary.to_csv(OUT / "anomaly_summary_by_market.csv", index=False, lineterminator="\n")
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
axes[0].hist(anomaly_score[anomaly_label == 1], bins=30, alpha=0.7, label="Typical", color="#2563eb")
axes[0].hist(anomaly_score[anomaly_label == -1], bins=30, alpha=0.7, label="Anomaly", color="#dc2626")
axes[0].set(title="Replay anomaly score distribution", xlabel="Isolation Forest decision score", ylabel="Rows")
axes[0].legend()
axes[0].grid(alpha=0.25)
rates = anomaly_out.groupby("anomaly_label")["shock_gt5"].mean().reindex(["typical", "anomaly"])
axes[1].bar(rates.index.astype(str), rates.values, color=["#2563eb", "#dc2626"])
axes[1].set(title="Observed rise rate by anomaly label (descriptive)", xlabel="Group", ylabel="Observed >5% rise rate", ylim=(0, 1))
axes[1].grid(axis="y", alpha=0.25)
savefig(fig, "anomaly_detection.png")

# 9) Existing expanding-window regression backtest, visualized as historical context.
backtest = pd.read_csv(backtest_path)
require_columns(backtest, ["year", "model", "MAE", "WAPE%"], backtest_path.name)
fig, axes = plt.subplots(1, 2, figsize=(12, 4.8))
for name, part in backtest.groupby("model"):
    part = part.sort_values("year")
    axes[0].plot(part["year"], part["MAE"], "o-", ms=3, label=name)
    axes[1].plot(part["year"], part["WAPE%"], "o-", ms=3, label=name)
axes[0].set(title="Historical regression error by test year", xlabel="Year", ylabel="MAE (source price units)")
axes[1].set(title="Historical weighted percentage error", xlabel="Year", ylabel="WAPE (%)")
for ax in axes:
    ax.grid(alpha=0.25)
    ax.legend(fontsize=7)
savefig(fig, "historical_forecast_error.png")

# Machine-readable run summary plus methodological guardrails.
run_info = {
    "product": "Yemen MarketShield AI",
    "analysis_script": "scripts/analyze_marketshield.py",
    "input_rows": int(len(pred)),
    "markets": int(pred["mkt_name"].nunique()),
    "validation_rows": int(len(validation)),
    "later_replay_rows": int(len(replay)),
    "validation_period_end": str(VALIDATION_END.date()),
    "later_replay_period_start": str(REPLAY_START.date()),
    "model_feature_columns": NUMERIC_FEATURES + [MARKET_FEATURE],
    "excluded_outcome_columns_from_features": ["shock_gt5", "next_pct_change", "next_date"],
    "threshold_tuning_uses_later_replay": False,
    "later_replay_is_untouched_independent_holdout": False,
    "pca_fit_window": "target months through 2021-12",
    "anomaly_model_fit_window": "target months through 2021-12",
    "interpretation": "Research/decision-support prototype; not validated for operational warning use.",
}
(OUT / "analysis_run_summary.json").write_text(json.dumps(run_info, indent=2) + "\n", encoding="utf-8")

# Output index with size checks to support clean handoff/review.
index = []
for path in sorted(OUT.iterdir()):
    if path.is_file() and path.name != "OUTPUT_INDEX.csv":
        index.append({"file": path.name, "bytes": path.stat().st_size})
pd.DataFrame(index).to_csv(OUT / "OUTPUT_INDEX.csv", index=False, lineterminator="\n")
print("\nANALYSIS COMPLETE")
print(f"Input rows: {len(pred)} | markets: {pred['mkt_name'].nunique()} | replay rows: {len(replay)}")
print(f"Model feature columns: {NUMERIC_FEATURES + [MARKET_FEATURE]}")
print("Outcome-derived columns excluded from features: shock_gt5, next_pct_change, next_date")
print(f"Output directory: {OUT}")
print(f"Artifacts written: {len(list(OUT.iterdir()))}")
