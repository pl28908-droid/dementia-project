"""SQLAlchemy tables for the SMARAN prototype."""
from datetime import datetime, date
from sqlalchemy import String, Integer, Float, DateTime, Date, ForeignKey, Text, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .database import Base

class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    display_name: Mapped[str] = mapped_column(String(80))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sessions = relationship("GameSession", back_populates="user", cascade="all, delete-orphan")
    memories = relationship("Memory", back_populates="user", cascade="all, delete-orphan")

class Game(Base):
    __tablename__ = "games"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(80), unique=True)
    game_type: Mapped[str] = mapped_column(String(40), unique=True)
    description: Mapped[str] = mapped_column(Text, default="")

class GameSession(Base):
    __tablename__ = "sessions"
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    game_type: Mapped[str] = mapped_column(String(40))
    difficulty: Mapped[str] = mapped_column(String(20))
    started_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    user = relationship("User", back_populates="sessions")
    performance = relationship("Performance", back_populates="session", uselist=False, cascade="all, delete-orphan")

class Performance(Base):
    __tablename__ = "performance"
    id: Mapped[int] = mapped_column(primary_key=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), unique=True)
    accuracy: Mapped[float] = mapped_column(Float)
    reaction_time_ms: Mapped[float] = mapped_column(Float)
    mistakes: Mapped[int] = mapped_column(Integer)
    completion_time_sec: Mapped[float] = mapped_column(Float)
    previous_score: Mapped[float] = mapped_column(Float, default=0)
    score: Mapped[float] = mapped_column(Float)
    predicted_band: Mapped[str | None] = mapped_column(String(30), nullable=True)
    session = relationship("GameSession", back_populates="performance")

class Memory(Base):
    __tablename__ = "memories"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    memory_text: Mapped[str] = mapped_column(Text)
    person: Mapped[str | None] = mapped_column(String(100), nullable=True)
    relationship_label: Mapped[str | None] = mapped_column(String(80), nullable=True)
    event_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="memories")

Index("ix_sessions_user_started", GameSession.user_id, GameSession.started_at)
