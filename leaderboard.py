from replit import db

class Leaderboard:
    def __init__(self):
        self.points = {}
    
    def add(self, player_id, points):
        self.points[str(player_id)] = self.points.setdefault(str(player_id), 0) + points
    
    def add_all(self, points):
        for player_id, score in points.items():
            self.add(player_id, score)

    def sort(self):
        self.points = dict(sorted(self.points.items(), key=lambda item: item[1], reverse=True))
        return self.points

    def save(self):
        db["leaderboard"] = self.points
    
    def load(self):
        if "leaderboard" in db.keys():
            self.points = db["leaderboard"]

