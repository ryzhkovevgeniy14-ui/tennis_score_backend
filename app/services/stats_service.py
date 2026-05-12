from sqlalchemy.ext.asyncio import AsyncSession
from app.models.player_stats import PlayerStats


class StatsService:
    """Сервис для обновления статистики игроков: геймы, сеты, рейтинг"""
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get_stats(self, player_id: int) -> PlayerStats:
        print(f'После этого попадаю в _get_stats')
        print(f'player_id={player_id}')
        stats = await self.session.get(PlayerStats, player_id)
        print(f"Статистика пока пустая stats = {stats}")
        if stats is None:
            print(f'Прохожу сравнение if not stats')
            stats = PlayerStats(
                player_id=player_id,
                games_won=0,
                games_lost=0,
                sets_won=0,
                sets_lost=0,
                rating_points=0
            )
            print('Пробую создать статистику')
            self.session.add(stats)
            await self.session.flush()
            print(f'Создал статистику,смотрю текущие выигранные геймы stats = {stats.games_won}')
            print(f"DEBUG: created new stats for player_id={player_id}")
        return stats

    # Обновление геймов
    async def update_game(self, winner_id: int, loser_id: int):
        print(f"После этого я попадаю в update_game")
        print(f'Где winner_id = {winner_id}, а loser_id = {loser_id}')
        winner = await self._get_stats(winner_id)
        winner.games_won += 1
        loser = await self._get_stats(loser_id)
        loser.games_lost += 1

    async def rollback_game(self, winner_id: int, loser_id: int):
        winner = await self._get_stats(winner_id)
        winner.games_won -= 1
        loser = await self._get_stats(loser_id)
        loser.games_lost -= 1

    # Обновление сетов
    async def update_set(self, winner_id: int, loser_id: int):
        winner = await self._get_stats(winner_id)
        winner.sets_won += 1
        loser = await self._get_stats(loser_id)
        loser.sets_lost += 1

    async def rollback_set(self, winner_id: int, loser_id: int):
        winner = await self._get_stats(winner_id)
        winner.sets_won -= 1
        loser = await self._get_stats(loser_id)
        loser.sets_lost -= 1

    # Обновление рейтинга
    async def update_rating(self, player_id: int, delta: int):
        stats = await self._get_stats(player_id)
        stats.rating_points += delta

    async def rollback_rating(self, player_id: int, delta: int):
        stats = await self._get_stats(player_id)
        stats.rating_points -= delta