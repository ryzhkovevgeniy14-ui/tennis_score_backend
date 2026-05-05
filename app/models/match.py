from sqlalchemy import String, DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player1_name: Mapped[str] = mapped_column(String(100), nullable=False)
    player2_name: Mapped[str] = mapped_column(String(100), nullable=False)
    games_p1: Mapped[int] = mapped_column(default=0)
    games_p2: Mapped[int] = mapped_column(default=0)
    sets_p1: Mapped[int] = mapped_column(default=0)
    sets_p2: Mapped[int] = mapped_column(default=0)
    set_number: Mapped[int] = mapped_column(default=1)
    tiebreak: Mapped[bool] = mapped_column(default=False)
    server_name: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)