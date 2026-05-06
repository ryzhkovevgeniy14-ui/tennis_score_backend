from pydantic import BaseModel, ConfigDict


class MatchCreate(BaseModel):
    player_1_name: str
    player_2_name: str


class Match(BaseModel):
    match_id: int
    players: list[str]
    current_set: dict[str, int]
    sets: list[int]
    history_sets: list[dict[str, int]]
    server: str

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    player: str
    count: int