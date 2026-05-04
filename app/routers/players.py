from fastapi import APIRouter, HTTPException, status

from app.schemas.player import PlayerCreate, Player as PlayerModel
from app.storage import storage


router = APIRouter(
    prefix="/players",
    tags=["players"]
)


@router.post("/", response_model=PlayerModel, status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerCreate):
    player_name = player.name.strip()

    for existing_player in storage.players:
        if existing_player.name.lower() == player_name.lower():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Игрок уже существует")

    player_id = storage.current_player_id
    new_player = PlayerModel(id=player_id, name=player_name)

    storage.players.append(new_player)
    storage.current_player_id += 1

    return new_player