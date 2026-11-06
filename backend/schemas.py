"""Pydantic request/response schemas."""
from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, Field

class UserCreate(BaseModel):
    display_name: str = Field(min_length=1, max_length=80)

class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    display_name: str
    created_at: datetime

class SessionCreate(BaseModel):
    user_id: int
    game_type: str
    difficulty: str = Field(pattern="^(easy|medium|hard)$")

class PerformanceCreate(BaseModel):
    session_id: int
    accuracy: float = Field(ge=0, le=1)
    reaction_time_ms: float = Field(gt=0, le=60000)
    mistakes: int = Field(ge=0)
    completion_time_sec: float = Field(gt=0, le=3600)
    previous_score: float = Field(ge=0, le=100)
    score: float = Field(ge=0, le=100)

class PredictionRequest(BaseModel):
    game_type: str
    difficulty: str
    accuracy: float = Field(ge=0, le=1)
    reaction_time_ms: float = Field(gt=0, le=60000)
    mistakes: int = Field(ge=0)
    completion_time_sec: float = Field(gt=0, le=3600)
    previous_score: float = Field(ge=0, le=100)
    score: float = Field(ge=0, le=100)

class MemoryCreate(BaseModel):
    user_id: int
    memory_text: str = Field(min_length=1, max_length=5000)
    person: str | None = Field(default=None, max_length=100)
    relationship_label: str | None = Field(default=None, max_length=80)
    event_date: date | None = None

class MemoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    memory_text: str
    person: str | None
    relationship_label: str | None
    event_date: date | None
    created_at: datetime
