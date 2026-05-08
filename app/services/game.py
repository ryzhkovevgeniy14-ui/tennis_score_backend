class GameService:
    def __init__(self, player1_name: str, player2_name: str):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.games = [0, 0]
        self.sets = [0, 0]
        self.server = player1_name
        self.tiebreak = False
        self.last_score_games = None
        self.last_server = None

    def change_games_score(self, player_name: str, count_games: int):
        # Запоминаем подающего ДО переключения
        old_server = self.server

        # Меняем подающего после каждого гейма
        if count_games != 0:
            self.server = self.player2_name if self.server == self.player1_name else self.player1_name

        # Изменяем счёт
        if player_name == self.player1_name:
            self.games[0] = max(0, self.games[0] + count_games)
        else:
            self.games[1] = max(0, self.games[1] + count_games)

        # Проверяем завершение сета
        self._check_set_completion(old_server)

    def _check_set_completion(self, server_before_point: str):
        player1_games, player2_games = self.games[0], self.games[1]

        # Проверка тайбрейка
        if player1_games == player2_games == 6:
            self.tiebreak = True
            return

        # Если сет завершается без тайбрейка
        if not self.tiebreak:
            if player1_games >= 6 and player1_games - player2_games >= 2:
                self._finish_set(self.player1_name, server_before_point)
            elif player2_games >= 6 and player2_games - player1_games >= 2:
                self._finish_set(self.player2_name, server_before_point)

        # Если сет завершается с тайбрейком
        else:
            if player1_games > player2_games:
                self._finish_set(self.player1_name, server_before_point)
            elif player2_games > player1_games:
                self._finish_set(self.player2_name, server_before_point)

    def _finish_set(self, winner_name: str, server_who_served_last_game: str):
        self.last_score_games = (self.games[0], self.games[1])
        self.last_server = server_who_served_last_game

        if self.tiebreak:
            self.tiebreak = False

        if winner_name == self.player1_name:
            self.sets[0] += 1
        else:
            self.sets[1] += 1

        self.games = [0, 0]
