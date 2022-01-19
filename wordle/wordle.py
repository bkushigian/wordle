from words import get_words


class Wordle:
    def __init__(self, word=None):
        self.word = word
        if word is None:
            self.word = get_words()
