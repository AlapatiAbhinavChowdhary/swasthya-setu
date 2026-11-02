"""Small SQLAlchemy persistence layer for API feedback and audit metadata."""

from datetime import datetime, timezone
from hashlib import sha256
from pathlib import Path

from sqlalchemy import Boolean, DateTime, Integer, String, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker


def hash_session_id(session_id: str) -> str:
    """Avoid storing a raw session identifier."""
    return sha256(session_id.encode("utf-8")).hexdigest()


class Base(DeclarativeBase):
    pass


class SessionRecord(Base):
    __tablename__ = "sessions"

    session_hash: Mapped[str] = mapped_column(String(64), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class MessageRecord(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_hash: Mapped[str] = mapped_column(String(64), index=True)
    role: Mapped[str] = mapped_column(String(20))
    message_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class FeedbackRecord(Base):
    __tablename__ = "feedback"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_hash: Mapped[str] = mapped_column(String(64), index=True)
    rating: Mapped[bool] = mapped_column(Boolean)
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    request_id: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class Database:
    """Create tables and expose short-lived SQLAlchemy sessions."""

    def __init__(self, database_path: str) -> None:
        path = Path(database_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        url = f"sqlite:///{path.as_posix()}"
        self.engine = create_engine(url, connect_args={"check_same_thread": False})
        self.session_factory = sessionmaker(bind=self.engine, expire_on_commit=False)
        Base.metadata.create_all(self.engine)

    def record_message(self, session_id: str, role: str, message: str) -> None:
        now = datetime.now(timezone.utc)
        session_hash = hash_session_id(session_id)
        with self.session_factory.begin() as db:
            record = db.get(SessionRecord, session_hash)
            if record is None:
                db.add(SessionRecord(
                    session_hash=session_hash,
                    created_at=now,
                    last_seen_at=now,
                ))
            else:
                record.last_seen_at = now
            db.add(MessageRecord(
                session_hash=session_hash,
                role=role,
                message_hash=sha256(message.encode("utf-8")).hexdigest(),
                created_at=now,
            ))

    def record_feedback(
        self,
        session_id: str,
        rating: bool,
        comment: str | None,
        request_id: str,
    ) -> None:
        with self.session_factory.begin() as db:
            db.add(FeedbackRecord(
                session_hash=hash_session_id(session_id),
                rating=rating,
                comment=comment,
                request_id=request_id,
                created_at=datetime.now(timezone.utc),
            ))
