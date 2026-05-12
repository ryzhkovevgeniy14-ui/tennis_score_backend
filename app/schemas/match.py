from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class MatchCreate(BaseModel):
    """
    Модель для создания матча.
    Используется в POST-запросах.
    """
    player1_name: Annotated[str, Field(description="Имя игрока 1")]
    player2_name: Annotated[str, Field(description="Имя игрока 2")]


class MatchResponse(BaseModel):
    """
    Модель для ответа с данными матча.
    Используется в GET-запросах.
    """
    id: Annotated[int, Field(description="ID матча")]
    player1_name: Annotated[str, Field(description="Имя игрока 1")]
    player2_name: Annotated[str, Field(description="Имя игрока 2")]
    games_p1: Annotated[int, Field(description="Количество геймов игрока 1")]
    games_p2: Annotated[int, Field(description="Количество геймов игрока 2")]
    sets_p1: Annotated[int, Field(description="Количество сетов игрока 1")]
    sets_p2: Annotated[int, Field(description="Количество сетов игрока 2")]
    tiebreak: Annotated[bool, Field(description="Наличие тайбрейка")]
    server_name: Annotated[str, Field(description="Подающий")]
    history_sets: Annotated[list[dict[str, int]], Field(default=[], description="История сыгранных сетов")]

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    """
    Модель для изменения счёта.
    Используется в POST-запросах.
    """
    player_name: Annotated[str, Field(description="Имя игрока")]
    count: Annotated[int, Field(description="Количество геймов")]