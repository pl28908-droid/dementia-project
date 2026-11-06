"""Business logic kept separate from HTTP route handlers."""
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import select
from . import models
from src.inference.predict import predict_one

ALLOWED_GAMES = {"memory_matching", "sequence_recall", "attention_test"}

def get_prediction(payload: dict) -> dict:
    return predict_one(payload)

def recommend_next_activity(db: Session, user_id: int) -> dict:
    latest = db.execute(
        select(models.GameSession)
        .where(models.GameSession.user_id == user_id)
        .order_by(models.GameSession.started_at.desc())
    ).scalars().first()

    if latest is None or latest.performance is None:
        return {
            "game_type": "memory_matching",
            "difficulty": "easy",
            "reason": "Start with a short introductory activity; no completed session is available yet."
        }

    band = latest.performance.predicted_band or "Moderate"
    if band == "Good":
        difficulty = "medium" if latest.difficulty == "easy" else "hard"
        reason = "The latest prototype performance band was Good; try a slightly more challenging activity."
    elif band == "Needs Attention":
        difficulty = "easy"
        reason = "The latest prototype performance band was Needs Attention; offer a simpler activity and allow a break."
    else:
        difficulty = latest.difficulty
        reason = "Keep the current difficulty and review performance over multiple sessions."

    next_game = {
        "memory_matching": "sequence_recall",
        "sequence_recall": "attention_test",
        "attention_test": "memory_matching",
    }.get(latest.game_type, "memory_matching")
    return {"game_type": next_game, "difficulty": difficulty, "reason": reason}
