from wordle import Wordle


def print_guess_result(guess):
    result = []
    for (let, status) in guess:
        if status == Wordle.HIT:
            result.append(f"\033[92m{let}\033[0m")
        elif status == Wordle.CLOSE:
            result.append(f"\033[93m{let}\033[0m")
        else:
            result.append(let)
    return ''.join(result)


def main():
    w = Wordle()
    guesses = []
    guess = ''
    while w.is_running():
        for g in guesses:
            print(f"       {print_guess_result(g)}")
        guess = input("\033[94;1mGuess> \033[0m")
        try:
            guesses.append(w.guess(guess))

        except RuntimeError as e:
            print(f"       \033[31;1m{str(e)}")
            if str(e).lower() == "game over":
                break
    for g in guesses:
        print(f"       {print_guess_result(g)}")
    if guess == w.word:
        print(f"\033[1;94mCongratulations!\033[0m You found the word \033[32;1m{w.word} \033[0m"
              f"in \033[32;1m{len(w.guesses)} tries\033[0m!!")
    else:
        print(f"\033[1;91mGame over!\033[0m The word you were looking for is \033[1;32m{w.word}\033[0m")


if __name__ == '__main__':
    main()
