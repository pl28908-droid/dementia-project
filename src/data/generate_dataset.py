"""Generate reproducible synthetic game-session data for development."""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "data" / "raw" / "synthetic_sessions.csv"

def generate_dataset(n_rows: int = 5000, random_state: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(random_state)
    game_types = np.array(["memory_matching", "sequence_recall", "attention_test"])
    difficulty = rng.choice(["easy", "medium", "hard"], size=n_rows, p=[0.35, 0.4, 0.25])
    game_type = rng.choice(game_types, size=n_rows)

    difficulty_penalty = pd.Series(difficulty).map({"easy": 0.00, "medium": 0.09, "hard": 0.19}).to_numpy()
    base = rng.normal(0.83, 0.13, n_rows) - difficulty_penalty
    accuracy = np.clip(base, 0.05, 1.0)

    reaction_time = rng.normal(1450, 420, n_rows) + difficulty_penalty * 900
    reaction_time += np.where(game_type == "sequence_recall", 180, 0)
    reaction_time = np.clip(reaction_time, 250, 6000)

    mistakes = rng.poisson(np.maximum(0.2, (1 - accuracy) * 9 + difficulty_penalty * 3))
    completion_time = rng.normal(52, 15, n_rows) + difficulty_penalty * 45 + mistakes * 1.7
    completion_time = np.clip(completion_time, 8, 240)

    previous_score = np.clip(rng.normal(65, 17, n_rows), 0, 100)
    score = np.clip(
        accuracy * 65
        + (1 - np.minimum(reaction_time, 5000) / 5000) * 15
        + (1 - np.minimum(mistakes, 12) / 12) * 10
        + previous_score * 0.10
        + rng.normal(0, 4, n_rows),
        0, 100
    )

    # Transparent, arbitrary software-demo label; not a clinical threshold.
    performance_band = np.where(
        (accuracy >= 0.78) & (score >= 68), "Good",
        np.where((accuracy >= 0.52) & (score >= 45), "Moderate", "Needs Attention")
    )

    df = pd.DataFrame({
        "age_group": rng.choice(["under_60", "60_69", "70_79", "80_plus"], n_rows),
        "game_type": game_type,
        "difficulty": difficulty,
        "accuracy": np.round(accuracy, 4),
        "reaction_time_ms": np.round(reaction_time, 1),
        "mistakes": mistakes.astype(int),
        "completion_time_sec": np.round(completion_time, 1),
        "previous_score": np.round(previous_score, 1),
        "score": np.round(score, 1),
        "performance_band": performance_band,
    })
    return df

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df = generate_dataset()
    df.to_csv(OUT, index=False)
    print(f"Saved {len(df):,} rows to {OUT}")
    print(df["performance_band"].value_counts(normalize=True).round(3))

if __name__ == "__main__":
    main()
