from hunspell import Hunspell
import string
import random
from replit import db

class WordGame:
    def __init__(self, leaderboard):
        self.leaderboard = leaderboard
        self.dict = Hunspell("en_GB", hunspell_data_dir="dictionaries")
        self.words = []
        self.last_player_id = None
        self.started = False

    def start(self):
        letter = random.choice(string.ascii_lowercase)
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

    def spellcheck(self, word):
        variants = [word, word.lower(), word.capitalize(), word.upper()]

        for variant in variants:
            if self.dict.spell(variant):
                return True
        return False

    def is_word_valid(self, word):
        return self.get_current_letter().lower() == word.lower()[0] and not self.is_word_used(word) and self.spellcheck(word)

    def is_last_player(self, player_id):
        return player_id == self.last_player_id

    def calculate_score(self, word):
        return len(word)

    def next_word(self, player_id, word):
        if not self.is_word_valid(word):
            return False

        self.last_player_id = player_id
        self.words.append(word)
        self.leaderboard.add(player_id, self.calculate_score(word))
        return True

    def has_started(self):
        return self.started

    def save(self):
        cur_game = {
            "words": self.words,
            "last_player_id": self.last_player_id,
            "started": self.started
        }

        db["cur_game"] = cur_game
    
    def load(self):
        if "cur_game" in db.keys():
            cur_game = db["cur_game"]
            self.words = cur_game["words"]
            self.last_player_id = cur_game["last_player_id"]
            self.started = cur_game["started"]