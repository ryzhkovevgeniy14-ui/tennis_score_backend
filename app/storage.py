from app.services.game import Match


class Storage:
    def __init__(self):
        self.current_player_id = 1
        self.current_match_id = 1
        self.players: list = []
        self.matches: dict[int, Match] = {}


storage = Storage()