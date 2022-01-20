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
    while w.is_running():
        for guess in guesses:
            print(f"       {print_guess_result(guess)}")
        guess = input("Guess> ")
        try:
            guesses.append(w.guess(guess))

        except RuntimeError as e:
            print(str(e))
            if str(e).lower() == "game over":
                break


if __name__ == '__main__':
    main()
