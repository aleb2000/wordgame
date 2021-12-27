import enchant
import string
import random
from replit import db

class WordGame():
    def __init__(self):
        self.points = {}
        self.dict = enchant.Dict("en")
        self.words = []
        self.last_player_id = None
        self.started = False

    def start(self):
        letter = random.choice(string.ascii_lowercase)
        self.points = {}
        self.words = [letter]
        self.last_player_id = None
        self.started = True
        return letter

    def end(self):
        self.started = False

    def get_current_letter(self):
        return self.words[-1][-1]

    def is_word_used(self, word):
        return word in self.words

    def is_word_valid(self, word):
        return self.get_current_letter() == word[0] and not self.is_word_used(word) and self.dict.check(word)

    def is_last_player(self, player_id):
        return player_id == self.last_player_id

    def add_points(self, player_id, points):
        if player_id in self.points:
            self.points[player_id] += points
        else:
            self.points[player_id] = points

    def calculate_score(self, word):
        return len(word)

    def next_word(self, player_id, word):
        if not self.is_word_valid(word):
            return False

        self.last_player_id = player_id
        self.words.append(word)
        self.add_points(player_id, self.calculate_score(word))
        return True

    def has_started(self):
        return self.started

    def save(self):
        cur_game = {
            "points": self.points,
            "words": self.words,
            "last_player_id": self.last_player_id,
            "started": self.started
        }

        db["cur_game"] = cur_game
    
    def load(self):
        if "cur_game" in db.keys():
            cur_game = db["cur_game"]
            self.points = cur_game["points"]
            self.words = cur_game["words"]
            self.last_player_id = cur_game["last_player_id"]
            self.started = cur_game["started"]