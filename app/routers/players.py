from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.schemas.player import PlayerCreate, Player as PlayerSchema
from app.models.player import Player as PlayerModel
from app.models.match import Match as MatchModel
from app.models.player_stats import PlayerStats
from app.db.depends import get_async_db


router = APIRouter(
    prefix="/players",
    tags=["players"]
)


@router.post("/", response_model=PlayerSchema, status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerCreate, session: AsyncSession = Depends(get_async_db)):
    """
    Добавление нового игрока
    """
    player_name = player.name.strip()

    # Проверяем есть ли уже такой игрок
    stmt = select(PlayerModel).where(func.lower(PlayerModel.name) == player_name.lower())
    result = await session.scalar(stmt)
    if result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Игрок уже существует")

    # Создаём нового игрока в БД
    new_player = PlayerModel(**player.model_dump())
    session.add(new_player)
    await session.commit()
    await session.refresh(new_player)

    return new_player


@router.get("/", response_model=list[PlayerSchema], status_code=status.HTTP_200_OK)
async def get_all_players(session: AsyncSession = Depends(get_async_db)):
    """
    Получение списка всех игроков
    """
    stmt = select(PlayerModel)
    result = await session.scalars(stmt)
    all_players = result.all()

    return all_players


@router.get("/{player_id}", response_model=PlayerSchema, status_code=status.HTTP_200_OK)
async def get_player(player_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Получение игрока по ID
    """
    stmt = select(PlayerModel).where(PlayerModel.id == player_id)
    player = await session.scalar(stmt)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Игрок не найден")

    return player


@router.get("/rating/")
async def get_players_rating(session: AsyncSession = Depends(get_async_db)):
    """
    Получение рейтинга всех игроков, отсортированного по убыванию
    """
    # Получаем всех игроков
    players_result = await session.execute(select(PlayerModel))
    players = players_result.scalars().all()

    # Получаем статистику
    stats_result = await session.execute(select(PlayerStats))
    stats_dict = {stat.player_id: stat for stat in stats_result.scalars().all()}

    # Формируем результат
    result = []
    for player in players:
        stats = stats_dict.get(player.id)
        rating = stats.rating_points if stats else 0
        result.append({
            "name": player.name,
            "rating": rating
        })

    # Сортируем по убыванию
    result.sort(key=lambda x: x["rating"], reverse=True)

    return result


@router.get("/{player_id}/stats")
async def get_player_stats(player_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Получение статистики игрока
    """
    # Получаем игрока
    player = await session.get(PlayerModel, player_id)
    if not player:
        raise HTTPException(404, "Игрок не найден")

    # Получаем статистику
    stats = await session.get(PlayerStats, player_id)

    # Получаем всех игроков для расчёта места в рейтинге
    all_players = await session.execute(select(PlayerModel))
    all_players_list = all_players.scalars().all()

    all_stats_result = await session.execute(select(PlayerStats))
    stats_dict = {stats.player_id: stats for stats in all_stats_result.scalars().all()}

    # Формируем список очков для сортировки
    points_list = []
    for player in all_players_list:
        points = stats_dict.get(player.id).rating_points if stats_dict.get(player.id) else 0
        points_list.append({"player_id": player.id, "points": points})

    # Сортируем по очкам (по убыванию) и определяем место
    points_list.sort(key=lambda x: x["points"], reverse=True)
    rating = next((i + 1 for i, points in enumerate(points_list) if points["player_id"] == player_id), None)

    if not stats:
        return {
            "name": player.name,
            "games": {"won": 0, "lost": 0, "percent": 0},
            "sets": {"won": 0, "lost": 0, "percent": 0},
            "points": 0,
            "rating": rating
        }

    total_games = stats.games_won + stats.games_lost
    total_sets = stats.sets_won + stats.sets_lost

    return {
        "name": player.name,
        "games": {
            "won": stats.games_won,
            "lost": stats.games_lost,
            "percent": round(stats.games_won / total_games * 100, 1) if total_games > 0 else 0
        },
        "sets": {
            "won": stats.sets_won,
            "lost": stats.sets_lost,
            "percent": round(stats.sets_won / total_sets * 100, 1) if total_sets > 0 else 0
        },
        "points": stats.rating_points,
        "rating": rating
    }


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Удаление игрока по ID
    """
    # Проверяем наличие игрока
    stmt = select(PlayerModel).where(PlayerModel.id == player_id)
    player = await session.scalar(stmt)
    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Игрок не найден")

    # Проверяем участвует ли игрок в матчах
    stmt = select(MatchModel).where(
        (MatchModel.player1_id == player_id) | (MatchModel.player2_id == player_id)
    )
    match = await session.scalar(stmt)
    if match:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Игрок участвует в матче")

    await session.delete(player)
    await session.commit()
    return