from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.schemas.match import MatchCreate, MatchResponse, GameUpdate
from app.models.match import Match as MatchModel
from app.models.player import Player as PlayerModel
from app.services.match_service import MatchService
from app.db.depends import get_async_db


router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(data: MatchCreate, session: AsyncSession = Depends(get_async_db)):
    """
    Создание нового матча
    """
    # Имена игроков при создании матча
    name_1 = data.player1_name.strip()
    name_2 = data.player2_name.strip()

    # Проверка наличия игроков с такими именами
    stmt_player1 = select(PlayerModel).where(func.lower(PlayerModel.name) == name_1.lower())
    stmt_player2 = select(PlayerModel).where(func.lower(PlayerModel.name) == name_2.lower())

    player_1 = await session.scalar(stmt_player1)
    player_2 = await session.scalar(stmt_player2)

    if not player_1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Игрок '{name_1}' не найден"
        )
    if not player_2:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Игрок '{name_2}' не найден"
        )

    if player_1.id == player_2.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Игрок не может играть сам с собой"
        )

    # Проверка на существующий матч между этими игроками
    new_players = {name_1.lower(), name_2.lower()}

    stmt_matches = select(MatchModel)

    existing_matches = await session.scalars(stmt_matches)
    for match in existing_matches:
        existing_players = {match.player1_name.lower(), match.player2_name.lower()}
        if existing_players == new_players:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Матч уже существует")

    # Создаём новый матч
    new_match = MatchModel(**data.model_dump())

    # Добавляем ID игроков и подающего вручную (в схеме их нет)
    new_match.player1_id = player_1.id
    new_match.player2_id = player_2.id
    new_match.server_name = player_1.name

    session.add(new_match)
    await session.commit()
    await session.refresh(new_match)

    service = MatchService(session)
    return await service.build_response(new_match)


@router.get("/", response_model=list[MatchResponse])
async def get_all_matches(session: AsyncSession = Depends(get_async_db)):
    """
    Получение списка всех игроков
    """
    matches = await session.scalars(select(MatchModel))
    service = MatchService(session)
    return [await service.build_response(match) for match in matches]


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Получение матча по ID
    """
    match = await session.get(MatchModel, match_id)
    if not match:
        raise HTTPException(404, "Матч не найден")

    service = MatchService(session)
    return await service.build_response(match)


@router.post("/{match_id}/add_game", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def add_game(match_id: int, data: GameUpdate, session: AsyncSession = Depends(get_async_db)):
    """
    Увеличение количества геймов
    """
    service = MatchService(session)
    return await service.modify_score(match_id, data.player_name, 1)


@router.post("/{match_id}/reduce_game", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def reduce_game(match_id: int, data: GameUpdate, session: AsyncSession = Depends(get_async_db)):
    """
    Уменьшение количества геймов (откат изменений)
    """
    service = MatchService(session)
    return await service.modify_score(match_id, data.player_name, -1)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Удаление матча по ID
    """
    stmt = select(MatchModel).where(MatchModel.id == match_id)
    match = await session.scalar(stmt)

    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Матч не найден")

    await session.delete(match)
    await session.commit()
    return