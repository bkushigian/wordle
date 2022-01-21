from words import get_random_word, is_valid_word


class Wordle:
    HIT = 0
    CLOSE = 1
    MISS = 2

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

        result = []
        game_won = True
        for (i, let) in enumerate(guess):
            if self.word[i] == let:
                result.append((let, Wordle.HIT))
            elif let in self.word:
                result.append((let, Wordle.CLOSE))
                game_won = False
            else:
                result.append((let, Wordle.MISS))
                game_won = False

        self.game_won = game_won
        self.guesses.append(result)
        return result

    def is_running(self):
        return len(self.guesses) < self.max_guesses and not self.game_won

    def give_up(self):
        while self.is_running():
            self.guesses.append("XXXXX")
        return self.word
