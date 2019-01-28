import sys, inspect
import random
import numpy as np

# Returns a list of all bot classes which inherit from the Bot class
def get_all_bots():
    return Bot.__subclasses__()

# The parent class for all bots
class Bot:

    def __init__(self, index, end_score):
        self.index = index
        self.end_score = end_score

    def update_state(self, current_throws):
        self.current_throws = current_throws

    def make_throw(self, scores, last_round):
        yield False


class ThrowTwiceBot(Bot):

    def make_throw(self, scores, last_round):
        yield True
        yield False

class GoToTenBot(Bot):

    def make_throw(self, scores, last_round):
        while sum(self.current_throws) < 10:
            yield True
        yield False