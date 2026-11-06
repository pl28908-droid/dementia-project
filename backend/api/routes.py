"""REST endpoints for profiles, sessions, ML inference and memory notes."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..database import get_db
from .. import models, schemas, services

router = APIRouter()

@router.post("/users", response_model=schemas.UserOut, status_code=201)
def create_user(payload: schemas.UserCreate, db: Session = Depends(get_db)):
    user = models.User(display_name=payload.display_name)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.get("/users/{user_id}", response_model=schemas.UserOut)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.get(models.User, user_id)
    if not user:
        raise HTTPException(404, "User not found")
    return user

@router.post("/sessions", status_code=201)
def create_session(payload: schemas.SessionCreate, db: Session = Depends(get_db)):
    if payload.game_type not in services.ALLOWED_GAMES:
        raise HTTPException(400, "Unsupported game_type")
    if not db.get(models.User, payload.user_id):
        raise HTTPException(404, "User not found")
    session = models.GameSession(**payload.model_dump())
    db.add(session)
    db.commit()
    db.refresh(session)
    return {"session_id": session.id, "status": "created"}

@router.post("/performance", status_code=201)
def record_performance(payload: schemas.PerformanceCreate, db: Session = Depends(get_db)):
    session = db.get(models.GameSession, payload.session_id)
    if not session:
        raise HTTPException(404, "Session not found")
    if session.performance:
        raise HTTPException(409, "Performance already recorded for this session")
    row = models.Performance(**payload.model_dump())
    session.completed_at = datetime.utcnow()
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"performance_id": row.id, "status": "recorded"}

@router.post("/predict")
def predict_performance(payload: schemas.PredictionRequest):
    try:
        return services.get_prediction(payload.model_dump())
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc))

@router.post("/sessions/{session_id}/predict")
def predict_and_attach(session_id: int, db: Session = Depends(get_db)):
    session = db.get(models.GameSession, session_id)
    if not session or not session.performance:
        raise HTTPException(404, "Session or performance record not found")
    p = session.performance
    payload = {
        "game_type": session.game_type,
        "difficulty": session.difficulty,
        "accuracy": p.accuracy,
        "reaction_time_ms": p.reaction_time_ms,
        "mistakes": p.mistakes,
        "completion_time_sec": p.completion_time_sec,
        "previous_score": p.previous_score,
        "score": p.score,
    }
    try:
        result = services.get_prediction(payload)
    except FileNotFoundError as exc:
        raise HTTPException(503, str(exc))
    p.predicted_band = result["performance_band"]
    db.commit()
    return result

@router.get("/history/{user_id}")
def get_history(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(404, "User not found")
    sessions = db.execute(
        select(models.GameSession)
        .where(models.GameSession.user_id == user_id)
        .order_by(models.GameSession.started_at.desc())
    ).scalars().all()
    return [{
        "session_id": s.id,
        "game_type": s.game_type,
        "difficulty": s.difficulty,
        "started_at": s.started_at,
        "completed_at": s.completed_at,
        "performance": None if not s.performance else {
            "accuracy": s.performance.accuracy,
            "score": s.performance.score,
            "predicted_band": s.performance.predicted_band,
        }
    } for s in sessions]

@router.get("/recommendations/{user_id}")
def get_recommendation(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(404, "User not found")
    return services.recommend_next_activity(db, user_id)

@router.post("/memories", response_model=schemas.MemoryOut, status_code=201)
def create_memory(payload: schemas.MemoryCreate, db: Session = Depends(get_db)):
    if not db.get(models.User, payload.user_id):
        raise HTTPException(404, "User not found")
    memory = models.Memory(**payload.model_dump())
    db.add(memory)
    db.commit()
    db.refresh(memory)
    return memory

@router.get("/memories/{user_id}", response_model=list[schemas.MemoryOut])
def list_memories(user_id: int, db: Session = Depends(get_db)):
    if not db.get(models.User, user_id):
        raise HTTPException(404, "User not found")
    return db.execute(
        select(models.Memory)
        .where(models.Memory.user_id == user_id)
        .order_by(models.Memory.created_at.desc())
    ).scalars().all()
