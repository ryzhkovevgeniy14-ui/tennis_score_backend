from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class SetHistory(Base):
    __tablename__ = 'sets_history'

    id: Mapped[int] = mapped_column(primary_key=True)
    match_id: Mapped[int] = mapped_column(ForeignKey("matches.id", ondelete="CASCADE"), nullable=False)
    set_number: Mapped[int] = mapped_column(nullable=False)
    player1_games: Mapped[int] = mapped_column(nullable=False)
    player2_games: Mapped[int] = mapped_column(nullable=False)
    server_name: Mapped[str] = mapped_column(String(100), nullable=False, server_default="")

    # Связь один ко многим (1 матч - много сетов)
    match: Mapped["Match"] = relationship(
        "Match",
        foreign_keys="SetHistory.match_id",
        back_populates="sets_history"
    )