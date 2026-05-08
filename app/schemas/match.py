from pydantic import BaseModel, ConfigDict


class MatchCreate(BaseModel):
    player1_name: str
    player2_name: str


class MatchResponse(BaseModel):
    id: int
    player1_name: str
    player2_name: str
    games_p1: int
    games_p2: int
    sets_p1: int
    sets_p2: int
    tiebreak: bool
    server_name: str
    history_sets: list[dict[str, int]] = []

    model_config = ConfigDict(from_attributes=True)


class GameUpdate(BaseModel):
    player_name: str
    count: int