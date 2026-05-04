class Match:
    def __init__(self, player_1_name: str, player_2_name: str):
        self.player_1_name = player_1_name
        self.player_2_name = player_2_name
        self.games = [0, 0]
        self.sets = [0, 0]
        self.set_number = 1
        self.tiebreak = False
        self.history_sets = []

        # Рейтинг отдельно для каждого игрока
        self.rating_p1 = 0
        self.rating_p2 = 0

        # Подающий (по умолчанию первый игрок)
        self.server = player_1_name

        # История для отмены действий
        self._history = []
        self._save_to_history()

    def _save_to_history(self):
        """Сохраняет текущее состояние, если оно отличается от последнего"""
        if self._history:
            last = self._history[-1]
            if (last['games'] == self.games and
                    last['sets'] == self.sets and
                    last['set_number'] == self.set_number and
                    last['tiebreak'] == self.tiebreak and
                    last['history_sets'] == self.history_sets and
                    last['rating_p1'] == self.rating_p1 and
                    last['rating_p2'] == self.rating_p2 and
                    last['server'] == self.server):
                return

        self._history.append({
            'games': self.games.copy(),
            'sets': self.sets.copy(),
            'set_number': self.set_number,
            'tiebreak': self.tiebreak,
            'history_sets': self.history_sets.copy(),
            'rating_p1': self.rating_p1,
            'rating_p2': self.rating_p2,
            'server': self.server
        })

    def undo(self):
        """Отменяет последнее действие"""
        if len(self._history) <= 1:
            return False

        # Удаляем текущее состояние
        self._history.pop()
        # Восстанавливаем предыдущее
        prev = self._history[-1]

        self.games = prev['games'].copy()
        self.sets = prev['sets'].copy()
        self.set_number = prev['set_number']
        self.tiebreak = prev['tiebreak']
        self.history_sets = prev['history_sets'].copy()
        self.rating_p1 = prev['rating_p1']
        self.rating_p2 = prev['rating_p2']
        self.server = prev['server']

        return True

    def change_games_score(self, player: str, count_games: int):
        # Сохраняем состояние ПЕРЕД изменением
        self._save_to_history()

        if player == self.player_1_name:
            new_score = self.games[0] + count_games
            if new_score >= 0:
                self.games[0] = new_score
                self.rating_p1 += 10 * count_games
        else:
            new_score = self.games[1] + count_games
            if new_score >= 0:
                self.games[1] = new_score
                self.rating_p2 += 10 * count_games

        # При изменении счёта (кроме 0) меняем подающего
        if count_games != 0:
            self.server = self.player_2_name if self.server == self.player_1_name else self.player_1_name

        self.check()

    def check(self):
        player_1_games = self.games[0]
        player_2_games = self.games[1]

        # Проверка тайбрейка
        if player_1_games == 6 and player_2_games == 6:
            self.tiebreak = True
            self._save_to_history()
            return

        # Сет без тайбрейка
        if not self.tiebreak:
            if player_1_games >= 6 and player_1_games - player_2_games >= 2:
                self.sets[0] += 1
                self.rating_p1 += 100

                self.history_sets.append({
                    self.player_1_name: self.games[0],
                    self.player_2_name: self.games[1]
                })

                self.set_number += 1
                self.reset()

            elif player_2_games >= 6 and player_2_games - player_1_games >= 2:
                self.sets[1] += 1
                self.rating_p2 += 100

                self.history_sets.append({
                    self.player_1_name: self.games[0],
                    self.player_2_name: self.games[1]
                })

                self.set_number += 1
                self.reset()

        # Сет с тайбрейком
        else:
            if player_1_games > player_2_games:
                self.sets[0] += 1
                self.rating_p1 += 100
            else:
                self.sets[1] += 1
                self.rating_p2 += 100

            self.history_sets.append({
                self.player_1_name: self.games[0],
                self.player_2_name: self.games[1]
            })

            self.set_number += 1
            self.reset()

        self._save_to_history()

    def reset(self):
        self.games = [0, 0]
        self.tiebreak = False

    def score(self):
        return {
            "players": [self.player_1_name, self.player_2_name],
            "current_set": {
                self.player_1_name: self.games[0],
                self.player_2_name: self.games[1],
            },
            "sets": self.sets,
            "history_sets": self.history_sets,
            "rating_p1": self.rating_p1,
            "rating_p2": self.rating_p2,
            "server": self.server
        }