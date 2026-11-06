"""Small reusable inference helper."""
from pathlib import Path
import joblib
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
MODEL_PATH = ROOT / "models" / "performance_pipeline.joblib"

def load_pipeline():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Model not found. Run python -m src.training.train first.")
    return joblib.load(MODEL_PATH)

def predict_one(payload: dict) -> dict:
    pipeline = load_pipeline()
    frame = pd.DataFrame([payload])
    label = pipeline.predict(frame)[0]
    result = {"performance_band": str(label)}
    if hasattr(pipeline, "predict_proba"):
        probabilities = pipeline.predict_proba(frame)[0]
        result["class_probabilities"] = {
            str(cls): round(float(prob), 4)
            for cls, prob in zip(pipeline.classes_, probabilities)
        }
    return result
