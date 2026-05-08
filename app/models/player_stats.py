from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class PlayerStats(Base):
    __tablename__ = "player_stats"

    player_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), primary_key=True)
    games_won: Mapped[int] = mapped_column(default=0)
    games_lost: Mapped[int] = mapped_column(default=0)
    sets_won: Mapped[int] = mapped_column(default=0)
    sets_lost: Mapped[int] = mapped_column(default=0)
    rating_points: Mapped[int] = mapped_column(default=0)

    # Связь один к одному (1 игрок - 1 набор статистики)
    player: Mapped["Player"] = relationship(
        "Player",
        back_populates="stats"
    )