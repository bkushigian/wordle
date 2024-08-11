from words import get_random_word, is_valid_word

HIT = 2
CLOSE = 1
MISS = 0

class Wordle:

    def __init__(self, word=None, max_guesses=6):
        self.word = word
        if word is None:
            self.word = get_random_word()
        self.guesses = []
        self.game_won = False
        self.max_guesses = max_guesses

    def guess(self, guess):
        if not is_valid_word(guess):
            raise RuntimeError(f"Invalid Word: {guess}")
        if len(self.guesses) >= self.max_guesses:
            raise RuntimeError("Game over")

        game_won = True
        hint = []
        for (i, let) in enumerate(guess):
            if self.word[i] == let:
                hint.append(HIT)
            elif let in self.word:
                hint.append(CLOSE)
                game_won = False
            else:
                hint.append(MISS)
                game_won = False

        self.game_won = game_won
        self.guesses.append((guess, hint))
        return tuple(hint)

    def is_running(self):
        return len(self.guesses) < self.max_guesses and not self.game_won

    def give_up(self):
        while self.is_running():
            self.guesses.append("XXXXX")
        return self.word
