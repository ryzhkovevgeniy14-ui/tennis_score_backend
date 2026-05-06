from pydantic import BaseModel, Field, ConfigDict


class PlayerCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, pattern=r'^[a-zA-Zа-яА-ЯёЁ\s\-]+$')


class Player(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)