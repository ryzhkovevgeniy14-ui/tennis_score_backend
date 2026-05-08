from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select

from app.schemas.match import MatchCreate, MatchResponse, GameUpdate
from app.models.match import Match as MatchModel
from app.models.player import Player as PlayerModel
from app.models.set_history import SetHistory
from app.services.game import GameService
from app.services.stats_service import StatsService
from app.db.depends import get_async_db


router = APIRouter(
    prefix="/matches",
    tags=["matches"],
)


async def _build_match_response(match: MatchModel, session: AsyncSession) -> MatchResponse:
    """Формирует MatchResponse с историей сетов"""
    # Загружаем историю сетов
    history_stmt = select(SetHistory).where(SetHistory.match_id == match.id).order_by(SetHistory.set_number)
    history = await session.scalars(history_stmt)
    history_list = [
        {match.player1_name: h.player1_games, match.player2_name: h.player2_games}
        for h in history
    ]

    return MatchResponse(
        id=match.id,
        player1_name=match.player1_name,
        player2_name=match.player2_name,
        games_p1=match.games_p1,
        games_p2=match.games_p2,
        sets_p1=match.sets_p1,
        sets_p2=match.sets_p2,
        tiebreak=match.tiebreak,
        server_name=match.server_name,
        history_sets=history_list
    )

async def _rollback_set(match: MatchModel, session: AsyncSession) -> MatchResponse:
    """
    Изменение счёта и статистики при откате сета
    """
    last_set_stmt = select(SetHistory).where(SetHistory.match_id == match.id).order_by(
        SetHistory.set_number.desc()).limit(1)
    last_set = await session.scalar(last_set_stmt)
    if not last_set:
        raise HTTPException(400, "Нет сета для отката")

    stats_service = StatsService(session)

    if last_set.player1_games > last_set.player2_games:
        match.sets_p1 -= 1
        match.games_p1 = last_set.player1_games - 1
        match.games_p2 = last_set.player2_games
        winner_id = match.player1_id
        loser_id = match.player2_id
    else:
        match.sets_p2 -= 1
        match.games_p1 = last_set.player1_games
        match.games_p2 = last_set.player2_games - 1
        winner_id = match.player2_id
        loser_id = match.player1_id

    match.tiebreak = False
    match.server_name = last_set.server_name

    # Откатываем последний гейм сета
    await stats_service.rollback_game(winner_id, loser_id)
    await stats_service.rollback_rating(winner_id, 10)

    # Откатываем сет
    await stats_service.rollback_set(winner_id, loser_id)
    await stats_service.rollback_rating(winner_id, 100)

    await session.delete(last_set)
    await session.commit()
    await session.refresh(match)

    return await _build_match_response(match, session)


async def _modify_score(match_id: int, player_name: str, delta: int, session: AsyncSession) -> MatchResponse:
    # Загружаем матч
    match = await session.get(MatchModel, match_id)
    if not match:
        raise HTTPException(404, "Матч не найден")

    # Откат сета (если delta == -1 и геймы 0:0)
    if delta == -1 and match.games_p1 == 0 and match.games_p2 == 0:
        return await _rollback_set(match, session)

    # --- Обычное изменение счёта ---
    old_games = (match.games_p1, match.games_p2)
    old_sets = (match.sets_p1, match.sets_p2)
    old_server = match.server_name

    # Создаём GameService
    game = GameService(match.player1_name, match.player2_name)
    game.games = [match.games_p1, match.games_p2]
    game.sets = [match.sets_p1, match.sets_p2]
    game.tiebreak = match.tiebreak
    game.server = match.server_name

    # Применяем изменение счёта
    game.change_games_score(player_name, delta)

    # Обновляем матч
    match.games_p1 = game.games[0]
    match.games_p2 = game.games[1]
    match.sets_p1 = game.sets[0]
    match.sets_p2 = game.sets[1]
    match.tiebreak = game.tiebreak
    match.server_name = game.server

    # Обновляем статистику геймов
    stats_service = StatsService(session)
    print("Я ДОШЁЛ ДО if delta == 1")
    if delta == 1:
        # Добавление гейма
        if player_name == match.player1_name:
            print(f"Я ПРОШЁЛ СРАВНЕНИЕ if match.games_p1 > old_games[0]")
            winner_id = int(match.player1_id)
            loser_id = int(match.player2_id)
            print(f"Я ПРИНТУЮ winner_id = {winner_id} с типом {type(winner_id)}")
            print(f"Я ПРИНТУЮ loser_id = {loser_id} с типом {type(loser_id)}")
        else:
            winner_id = int(match.player2_id)
            loser_id = int(match.player1_id)

        await stats_service.update_game(winner_id, loser_id)
        await stats_service.update_rating(winner_id, 10)

    elif delta == -1:
        # Уменьшение гейма
        if player_name == match.player1_name:
            winner_id = int(match.player1_id)
            loser_id = int(match.player2_id)
        else:
            winner_id = int(match.player2_id)
            loser_id = int(match.player1_id)

        await stats_service.rollback_game(winner_id, loser_id)
        await stats_service.rollback_rating(winner_id, 10)

    # Если завершился сет — сохраняем в историю и обновляем статистику сетов
    if (match.sets_p1 > old_sets[0]) or (match.sets_p2 > old_sets[1]):
        new_set = SetHistory(
            match_id=match_id,
            set_number=match.sets_p1 + match.sets_p2,
            player1_games=game.last_score_games[0],
            player2_games=game.last_score_games[1],
            server_name=old_server
        )
        session.add(new_set)

        # Обновляем статистику сетов
        if match.sets_p1 > old_sets[0]:
            await stats_service.update_set(match.player1_id, match.player2_id)
            await stats_service.update_rating(match.player1_id, 100)
        else:
            await stats_service.update_set(match.player2_id, match.player1_id)
            await stats_service.update_rating(match.player2_id, 100)

    await session.commit()
    await session.refresh(match)

    return await _build_match_response(match, session)


@router.post("/", response_model=MatchResponse, status_code=status.HTTP_201_CREATED)
async def create_match(data: MatchCreate, session: AsyncSession = Depends(get_async_db)):
    """
    Создание нового матча.
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
    new_players = {name_1, name_2}

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

    return await _build_match_response(new_match, session)


@router.get("/", response_model=list[MatchResponse])
async def get_all_matches(session: AsyncSession = Depends(get_async_db)):
    stmt = select(MatchModel)
    matches = await session.scalars(stmt)

    all_matches = []
    for match in matches:
        all_matches.append(await _build_match_response(match, session))

    return all_matches


@router.get("/{match_id}", response_model=MatchResponse)
async def get_match(match_id: int, session: AsyncSession = Depends(get_async_db)):
    stmt = select(MatchModel).where(MatchModel.id == match_id)
    match = await session.scalar(stmt)

    if not match:
        raise HTTPException(404, "Матч не найден")

    return await _build_match_response(match, session)


@router.post("/{match_id}/add_game", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def add_game(match_id: int, data: GameUpdate, session: AsyncSession = Depends(get_async_db)):
    """
    Увеличиваем геймы
    """
    return await _modify_score(match_id, data.player_name, 1, session)


@router.post("/{match_id}/reduce_game", response_model=MatchResponse, status_code=status.HTTP_200_OK)
async def reduce_game(match_id: int, data: GameUpdate, session: AsyncSession = Depends(get_async_db)):
    """
    Уменьшение количества геймов (откат изменений)
    """
    return await _modify_score(match_id, data.player_name, -1, session)


@router.delete("/{match_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_match(match_id: int, session: AsyncSession = Depends(get_async_db)):
    """
    Удаление матча по ID.
    """
    stmt = select(MatchModel).where(MatchModel.id == match_id)
    match = await session.scalar(stmt)

    if not match:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Матч не найден")

    await session.delete(match)
    await session.commit()
    return