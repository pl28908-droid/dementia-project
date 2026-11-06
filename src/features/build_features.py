"""Central feature definitions used by training and inference."""
NUMERIC_FEATURES = [
    "accuracy",
    "reaction_time_ms",
    "mistakes",
    "completion_time_sec",
    "previous_score",
    "score",
]
CATEGORICAL_FEATURES = ["game_type", "difficulty"]
TARGET = "performance_band"
