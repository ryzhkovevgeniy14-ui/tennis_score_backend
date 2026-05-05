from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from app.db.base import Base


class SetHistory(Base):
    __tablename__ = "sets_history"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    set_number: Mapped[int] = mapped_column(nullable=False)
    player1_games: Mapped[int] = mapped_column(nullable=False)
    player2_games: Mapped[int] = mapped_column(nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)