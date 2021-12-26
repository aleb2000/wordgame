import enchant
import string
import random

class WordGame():
    def __init__(self):
        self.points = {}
        self.dict = enchant.Dict("en")
        self.words = []
        self.last_player = None
        self.started = False

    def start(self):
        letter = random.choice(string.ascii_lowercase)
        self.points = {}
        self.words = [letter]
        self.last_player = None
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

    def is_last_player(self, player):
        return player == self.last_player

    def add_points(self, player, points):
        if player in self.points:
            self.points[player] += points
        else:
            self.points[player] = points

    def calculate_score(self, word):
        return len(word)

    def next_word(self, player, word):
        if not self.is_word_valid(word):
            return False

        self.last_player = player
        self.words.append(word)
        self.add_points(player, self.calculate_score(word))
        return True

    def has_started(self):
        return self.started
