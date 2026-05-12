from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Player(Base):
    """
    Модель игрока
    """
    __tablename__ = "players"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)


    # Связь один ко многим (много матчей - 1 игрок)
    matches_player1: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="Match.player1_id",
        back_populates="player1"
    )
    matches_player2: Mapped[list["Match"]] = relationship(
        "Match",
        foreign_keys="Match.player2_id",
        back_populates="player2"
    )

    # Связь один к одному (1 набор статистики для 1 игрока)
    stats: Mapped["PlayerStats"] = relationship(
        "PlayerStats",
        back_populates="player",
        uselist=False
    )