"""Train and compare reproducible Scikit-learn pipelines."""
from pathlib import Path
import json
import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src.features.build_features import NUMERIC_FEATURES, CATEGORICAL_FEATURES, TARGET

ROOT = Path(__file__).resolve().parents[2]
DATA_PATH = ROOT / "data" / "raw" / "synthetic_sessions.csv"
MODEL_PATH = ROOT / "models" / "performance_pipeline.joblib"
REPORT_PATH = ROOT / "reports" / "training_metrics.json"

def make_preprocessor():
    numeric_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler()),
    ])
    categorical_pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore")),
    ])
    return ColumnTransformer([
        ("numeric", numeric_pipe, NUMERIC_FEATURES),
        ("categorical", categorical_pipe, CATEGORICAL_FEATURES),
    ])

def main():
    if not DATA_PATH.exists():
        raise FileNotFoundError("Dataset missing. Run: python -m src.data.generate_dataset")

    df = pd.read_csv(DATA_PATH)
    X = df[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
    y = df[TARGET]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    candidates = {
        "logistic_regression": LogisticRegression(max_iter=1500, class_weight="balanced"),
        "random_forest": RandomForestClassifier(
            n_estimators=300, max_depth=None, min_samples_leaf=2,
            class_weight="balanced_subsample", random_state=42, n_jobs=-1
        ),
    }

    results = {}
    best_name, best_pipeline, best_f1 = None, None, -1
    for name, estimator in candidates.items():
        pipeline = Pipeline([
            ("preprocessor", make_preprocessor()),
            ("classifier", estimator),
        ])
        pipeline.fit(X_train, y_train)
        predictions = pipeline.predict(X_test)
        macro_f1 = f1_score(y_test, predictions, average="macro")
        results[name] = {
            "macro_f1": float(macro_f1),
            "classification_report": classification_report(
                y_test, predictions, output_dict=True, zero_division=0
            ),
            "confusion_matrix": confusion_matrix(
                y_test, predictions, labels=["Good", "Moderate", "Needs Attention"]
            ).tolist(),
        }
        print(f"{name}: macro-F1={macro_f1:.4f}")
        if macro_f1 > best_f1:
            best_name, best_pipeline, best_f1 = name, pipeline, macro_f1

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(best_pipeline, MODEL_PATH)
    report = {
        "selected_model": best_name,
        "selected_macro_f1": float(best_f1),
        "candidate_results": results,
        "note": "Synthetic rule-generated labels; metrics are for pipeline demonstration only, not clinical validity."
    }
    REPORT_PATH.write_text(json.dumps(report, indent=2))
    print(f"Selected: {best_name}")
    print(f"Saved pipeline: {MODEL_PATH}")
    print(f"Saved metrics: {REPORT_PATH}")

if __name__ == "__main__":
    main()
