from words import *
from wordle import Wordle
from cli import print_guess_result
from statistics import mean, median, mode
from argparse import ArgumentParser
from random import choice


def next_guess(ws, top=1):
    choices = get_top_n_words_by_freqs(ws, top)
    return choice(choices)[0]


def apply_hint(hint, ws):
    misses = []
    closes = []
    hits = []
    for i, (letter, status) in enumerate(hint):
        if status == Wordle.MISS:
            misses.append(letter)
        elif status == Wordle.HIT:
            hits.append((letter, i))
        elif status == Wordle.CLOSE:
            closes.append((letter, i))
        else:
            raise RuntimeError("Unknown hint status " + str(status))

    misses = ''.join(misses)
    ws = omit_letters(misses, ws)
    ws = with_letters_at_positions(hits, ws)
    ws = with_letters_not_at_positions(closes, ws)
    return ws


def solve(w: Wordle, verbose=False, algorithm="best-first-two-guesses"):
    if algorithm == "max-frequency":
        return solve_with_max_frequencies(w, verbose)
    elif algorithm == "best-first-two-guesses":
        return solve_with_best_first_two_guesses(w, verbose)
    else:
        return solve_with_max_frequencies(w, verbose)


def solve_with_best_first_two_guesses(w: Wordle, verbose=False):
    ws = get_words()
    while w.is_running():
        if verbose:
            print(f"--- Round {len(w.guesses) + 1}: {len(ws)} words remaining ---")

        if not w.guesses:
            # First guess is always 'arose'
            g = "arose"
        elif len(w.guesses) == 1:
            # Second guess is always 'until'
            g = "until"
        else:
            # after that, pick top 4 best matches randomly
            g = next_guess(ws, top=4)

        try:
            hint = w.guess(g)
            if verbose:
                print(f"    {print_guess_result(hint)}")
            ws = apply_hint(hint, ws)
        except RuntimeError as e:
            print(str(e))

    if not w.game_won:
        print(f"Lost game: {w.word} with {len(w.guesses)} guesses")
    return len(w.guesses), w.game_won


def solve_with_max_frequencies(w: Wordle, verbose=False):
    ws = get_words()
    while w.is_running():
        if verbose:
            print(f"--- Round {len(w.guesses) + 1}: {len(ws)} words remaining ---")
        if not w.guesses:
            # First guess can be any top 40
            g = next_guess(ws, top=40)
        else:
            g = next_guess(ws, top=4)
        try:
            hint = w.guess(g)
            if verbose:
                print(f"    {print_guess_result(hint)}")
            ws = apply_hint(hint, ws)
        except RuntimeError as e:
            print(str(e))

    if not w.game_won:
        print(f"Lost game: {w.word} with {len(w.guesses)} guesses")
    return len(w.guesses), w.game_won


def run_batch(n=500, verbose=False, word=None, max_guesses=6, algorithm='max-frequency'):
    runs = []

    for i in range(n):
        if word is None:
            w = Wordle(max_guesses=max_guesses)
        else:
            w = Wordle(word, max_guesses=max_guesses)
        if verbose:
            print(f"===== Word {i + 1} of {n}: Target Word is \033[1m{w.word}\033[0m =====")
        runs.append(solve(w, verbose=verbose, algorithm=algorithm))

    return runs


def interactive():
    ws = get_words()
    i = 1
    unknown_positions = [0, 1, 2, 3, 4]  # Positions whose values we don't know yet
    while True:
        print(f"--- Round {i}: {len(ws)} words remaining ---")
        if i == 1:
            # First guess can be any top 40
            g = next_guess(ws, top=40)
        else:
            g = next_guess(ws, top=2)
        print("Guess: " + g)
        try:
            hint = None
            invalid_input = True
            while invalid_input:
                invalid_input = False
                hint = []
                feedback = input("\033[34;1mEnter feedback (? for help)>\033[0m ").strip()
                codes = {'G': Wordle.HIT, 'g': Wordle.HIT,
                         'Y': Wordle.CLOSE, 'y': Wordle.CLOSE,
                         'B': Wordle.MISS, 'b': Wordle.MISS}
                if feedback == '?':
                    print("For each letter in your guess, write:\n"
                          " - 'G' if it was green,\n"
                          " - 'Y' if it was yellow, and\n"
                          " - 'B' if ti was black")
                    invalid_input = True
                elif len(feedback) == 5:
                    for fb, let in zip(feedback, g):
                        if fb not in codes:
                            print(f"Invalid feedback character: {fb}")
                            invalid_input = True
                            break
                        hint.append((let, codes[fb]))
                else:
                    print("Invalid feedback: length must be 5")
                    invalid_input = True

            print(f"    {print_guess_result(hint)}")
            ws = apply_hint(hint, ws)
        except RuntimeError as e:
            print(str(e))


def report_stats(runs):
    no_runs = len(runs)
    wins = [gs for (gs, w) in runs if w]
    no_wins = len(wins)
    no_losses = no_runs - no_wins
    mean_guesses_in_wins = mean(wins)
    mode_guesses_in_wins = mode(wins)
    median_guesses_in_wins = median(wins)

    print(f"Runs: {no_runs}")
    print(f"Wins: {no_wins} ({100 * no_wins / no_runs}%)    Losses: {no_losses} ({100 * no_losses / no_runs}%)")
    print(f"Num Guesses")
    print(f"    Min:    {min(wins)}")
    print(f"    Max:    {max(wins)}")
    print(f"    Mean:   {mean_guesses_in_wins}")
    print(f"    Median: {median_guesses_in_wins}")
    print(f"    Mode:   {mode_guesses_in_wins}")


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Print intermediate run information")
    parser.add_argument("--word", default=None, help="Set Wordle word to try to solve. This results in a single run")
    parser.add_argument("-s", "--batch_size", default=500, type=int, help="Batch size for running stats")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run an interactive session")
    parser.add_argument("-m", "--max-guesses", default=6, type=int, help="Maximum number of allowed guesses")
    parser.add_argument("-a", "--algorithm", default="max-frequency", help="Algorithm to use")

    args = parser.parse_args()
    if args.interactive:
        interactive()
        return
    else:
        runs = run_batch(args.batch_size, verbose=args.verbose, word=args.word, max_guesses=args.max_guesses,
                         algorithm=args.algorithm)

    report_stats(runs)


if __name__ == '__main__':
    main()






