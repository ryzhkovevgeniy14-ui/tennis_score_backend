from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Match(Base):
    """
    Модель матча
    """
    __tablename__ = "matches"

    id: Mapped[int] = mapped_column(primary_key=True)
    player1_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player2_id: Mapped[int] = mapped_column(ForeignKey("players.id", ondelete="CASCADE"), nullable=False)
    player1_name: Mapped[str] = mapped_column(String(100), nullable=False)
    player2_name: Mapped[str] = mapped_column(String(100), nullable=False)
    games_p1: Mapped[int] = mapped_column(default=0)
    games_p2: Mapped[int] = mapped_column(default=0)
    sets_p1: Mapped[int] = mapped_column(default=0, server_default="0")
    sets_p2: Mapped[int] = mapped_column(default=0, server_default="0")
    tiebreak: Mapped[bool] = mapped_column(nullable=False, server_default="false")
    server_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")

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

    # Связь один ко многим (1 матч - много сетов)
    sets_history: Mapped[list["SetHistory"]] = relationship(
        "SetHistory",
        foreign_keys="SetHistory.match_id",
        back_populates="match",
        cascade="all, delete-orphan"
    )