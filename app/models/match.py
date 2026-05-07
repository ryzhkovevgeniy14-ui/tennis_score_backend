from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Match(Base):
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player1_name: Mapped[str] = mapped_column(String(100), nullable=False)
    player2_name: Mapped[str] = mapped_column(String(100), nullable=False)
    games_p1: Mapped[int] = mapped_column(default=0)
    games_p2: Mapped[int] = mapped_column(default=0)

    # Связь один ко многим (много матчей - 1 игрок)
    player1: Mapped["Player"] = relationship(
        "Player",
        foreign_keys="Match.player1_id",
        back_populates="matches_player1"
    )
    player2: Mapped["Player"] = relationship(
        "Player",
        foreign_keys="Match.player2_id",
        back_populates="matches_player2"
    )