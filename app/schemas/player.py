from pydantic import BaseModel, Field, ConfigDict
from typing import Annotated


class PlayerCreate(BaseModel):
    """
    Модель для добавления игрока.
    Используется в POST-запросах.
    """
    name: Annotated[
        str,
        Field(
            min_length=1,
            max_length=50,
            pattern=r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$',
            description="Имя игрока"
        )
    ]


class Player(BaseModel):
    """
    Модель для ответа с данными игрока.
    Используется в GET-запросах.
    """
    id: Annotated[int, Field(description="ID игрока")]
    name: Annotated[str, Field(description="Имя игрока")]

    model_config = ConfigDict(from_attributes=True)