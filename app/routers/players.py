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


@router.get("/", response_model=list[PlayerModel], status_code=status.HTTP_200_OK)
async def get_all_players():
    return storage.players


@router.get("/{player_id}", response_model=PlayerModel, status_code=status.HTTP_200_OK)
async def get_player(player_id: int):
    for player in storage.players:
        if player.id == player_id:
            return player

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Игрок не найден")


@router.get("/rating/")
async def get_players_rating():
    """Возвращает рейтинг всех игроков, отсортированный по убыванию"""
    rating_dict = {}

    # Сначала добавляем всех игроков с рейтингом 0
    for player in storage.players:
        rating_dict[player.name] = 0

    # Потом добавляем рейтинг из матчей
    for match in storage.matches.values():
        rating_dict[match.player_1_name] = rating_dict.get(match.player_1_name, 0) + match.rating_p1
        rating_dict[match.player_2_name] = rating_dict.get(match.player_2_name, 0) + match.rating_p2

    # Преобразуем в список
    result = [
        {"name": name, "rating": rating}
        for name, rating in rating_dict.items()
    ]

    # Сортировка по убыванию
    result.sort(key=lambda x: x["rating"], reverse=True)

    return result


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int):
    # Найти игрока
    player_to_delete = None
    for player in storage.players:
        if player.id == player_id:
            player_to_delete = player
            break

    if not player_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Игрок не найден")

    # Проверить, участвует ли в матчах
    for match in storage.matches.values():
        if player_to_delete.name in [match.player_1_name, match.player_2_name]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Нельзя удалить игрока: он участвует в матче"
            )

    storage.players.remove(player_to_delete)
    return