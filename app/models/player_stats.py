from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import datetime

from app.db.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    games_won: Mapped[int] = mapped_column(default=0)
    games_lost: Mapped[int] = mapped_column(default=0)
    sets_won: Mapped[int] = mapped_column(default=0)
    sets_lost: Mapped[int] = mapped_column(default=0)
    rating_points: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    # Связь обратно к игроку
    player = relationship("Player", back_populates="stats")