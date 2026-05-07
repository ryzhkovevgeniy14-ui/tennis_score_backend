class GameService:
    def __init__(self, player1_name: str, player2_name: str):
        self.player1_name = player1_name
        self.player2_name = player2_name
        self.games = [0, 0]
        self.tiebreak = False

    def change_games_score(self, player_name: str, count_games: int):
        if player_name == self.player1_name:
            self.games[0] = max(0, self.games[0] + count_games)
        else:
            self.games[1] = max(0, self.games[1] + count_games)