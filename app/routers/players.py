from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.schemas.player import PlayerCreate, Player as PlayerSchema
from app.models.player import Player as PlayerModel
from app.models.match import Match as MatchModel
from app.db.depends import get_async_db


router = APIRouter(
    prefix="/players",
    tags=["players"]
)


@router.post("/", response_model=PlayerSchema, status_code=status.HTTP_201_CREATED)
async def create_player(player: PlayerCreate, session: AsyncSession = Depends(get_async_db)):
    """
    Добавляет нового игрока.
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
    Возвращает список всех игроков.
    """
    stmt = select(PlayerModel)
    result = await session.scalars(stmt)
    all_players = result.all()

    return all_players


@router.get("/{player_id}", response_model=PlayerSchema, status_code=status.HTTP_200_OK)
async def get_player(player_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Возвращает игрока по ID.
    """
    stmt = select(PlayerModel).where(PlayerModel.id == player_id)
    player = await session.scalar(stmt)

    if not player:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Игрок не найден")

    return player


@router.delete("/{player_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_player(player_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Удаление игрока по ID.
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