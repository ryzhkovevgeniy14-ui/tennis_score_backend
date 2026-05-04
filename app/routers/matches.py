from fastapi import APIRouter, HTTPException, status

from app.schemas.match import MatchCreate, Match as MatchModel, GameUpdate
from app.services.game import Match
from app.storage import storage


router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)


@router.post("/", response_model= MatchModel, status_code=status.HTTP_201_CREATED)
async def create_match(data: MatchCreate):
    player_1 = next((player for player in storage.players
                     if player.name.lower() == data.player_1_name.lower().strip()), None)
    player_2 = next((player for player in storage.players
                     if player.name.lower() == data.player_2_name.lower().strip()), None)

    if not player_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Игрок '{data.player_1_name}' не найден"
        )
    if not player_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Игрок '{data.player_2_name}' не найден"
        )

    if player_1.id == player_2.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Игрок не может играть сам с собой"
        )

    # защита от дублирующего матча (A vs B == B vs A)
    new_players = {player_1.name.lower(), player_2.name.lower()}

    for existing_match in storage.matches.values():
        existing_players = {
            existing_match.player_1_name.lower(),
            existing_match.player_2_name.lower()
        }

        if existing_players == new_players:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Матч уже существует"
            )

    match_id = storage.current_match_id
    match = Match(player_1.name, player_2.name)

    storage.matches[match_id] = match
    storage.current_match_id += 1

    return {
        "match_id": match_id,
        **match.score()
    }


@router.get("/", response_model=list[MatchModel], status_code=status.HTTP_200_OK)
async def get_all_matches():
    return [
        {"match_id": match_id, **match.score()}
        for match_id, match in storage.matches.items()
    ]


@router.get("/{match_id}", response_model=MatchModel, status_code=status.HTTP_200_OK)
async def get_match(match_id: int):
    match = storage.matches.get(match_id)

    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Матч не найден")

    return {
        "match_id": match_id,
        **match.score()
    }


@router.post("/{match_id}/score", response_model=MatchModel, status_code=status.HTTP_200_OK)
async def add_game(match_id: int, data: GameUpdate):
    match = storage.matches.get(match_id)

    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Матч не найден")

    match.change_games_score(data.player, data.count)

    return {
        "match_id": match_id,
        **match.score()
    }