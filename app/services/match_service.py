from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.schemas.match import MatchResponse
from app.models.match import Match as MatchModel
from app.models.set_history import SetHistory
from app.services.game_service import GameService
from app.services.stats_service import StatsService


class MatchService:
    """Сервис для работы с матчами: изменение счёта, откат сетов, формирование ответа"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def build_response(self, match: MatchModel) -> MatchResponse:
        """Формирует MatchResponse с историей сетов"""
        # Загружаем историю сетов
        history_stmt = select(SetHistory).where(SetHistory.match_id == match.id).order_by(SetHistory.set_number)
        history = await self.session.scalars(history_stmt)
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

    async def rollback_set(self, match: MatchModel) -> MatchResponse:
        """
        Изменение счёта и статистики при откате сета
        """
        last_set_stmt = (select(SetHistory)
                         .where(SetHistory.match_id == match.id)
                         .order_by(SetHistory.set_number.desc())
                         .limit(1)
                         )
        last_set = await self.session.scalar(last_set_stmt)
        if not last_set:
            raise HTTPException(400, "Нет сета для отката")

        stats_service = StatsService(self.session)

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

        await self.session.delete(last_set)
        await self.session.commit()
        await self.session.refresh(match)

        return await self.build_response(match)

    async def modify_score(self, match_id: int, player_name: str, delta: int) -> MatchResponse:
        """Основная логика изменения счёта"""
        match = await self.session.get(MatchModel, match_id)
        if not match:
            raise HTTPException(404, "Матч не найден")

        # Откат сета
        if delta == -1 and match.games_p1 == 0 and match.games_p2 == 0:
            return await self.rollback_set(match)

        # Обычное изменение счёта
        old_sets = (match.sets_p1, match.sets_p2)
        old_server = match.server_name

        # Создаём экземпляр GameService
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
        stats_service = StatsService(self.session)

        # Увеличение геймов
        if delta == 1:
            winner_id = match.player1_id if player_name == match.player1_name else match.player2_id
            loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id
            await stats_service.update_game(winner_id, loser_id)
            await stats_service.update_rating(winner_id, 10)

        # Уменьшение геймов
        elif delta == -1:
            winner_id = match.player1_id if player_name == match.player1_name else match.player2_id
            loser_id = match.player2_id if winner_id == match.player1_id else match.player1_id
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
            self.session.add(new_set)

            # Обновляем статистику сетов
            if match.sets_p1 > old_sets[0]:
                await stats_service.update_set(match.player1_id, match.player2_id)
                await stats_service.update_rating(match.player1_id, 100)
            else:
                await stats_service.update_set(match.player2_id, match.player1_id)
                await stats_service.update_rating(match.player2_id, 100)

        await self.session.commit()
        await self.session.refresh(match)

        return await self.build_response(match)

