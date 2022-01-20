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


def solve(w: Wordle, verbose=False):
    ws = get_words()
    while w.is_running():
        if verbose:
            print(f"--- Round {len(w.guesses) + 1}: {len(ws)} words remaining ---")
        if not w.guesses:
            # First guess can be any top 40
            g = next_guess(ws, top=40)
        else:
            g = next_guess(ws, top=2)
        try:
            hint = w.guess(g)
            if verbose:
                print(f"    {print_guess_result(hint)}")
            ws = apply_hint(hint, ws)
        except RuntimeError as e:
            print(str(e))

    return len(w.guesses), w.game_won


def run_batch(n=500, verbose=False):
    runs = []
    for i in range(n):
        w = Wordle()
        if verbose:
            print(f"===== Word {i + 1} of {n}: Target Word is \033[1m{w.word}\033[0m =====")
        runs.append(solve(w, verbose=verbose))

    return runs


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
    print(f"    Mean:   {mean_guesses_in_wins}")
    print(f"    Median: {median_guesses_in_wins}")
    print(f"    Mode:   {mode_guesses_in_wins}")


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Print intermediate run information")
    parser.add_argument("--word", default=None, help="Set Wordle word to try to solve. This results in a single run")
    parser.add_argument("-s", "--batch_size", default=500, type=int, help="batch size for running stats")

    args = parser.parse_args()
    if args.word is not None:
        w = Wordle(args.word)
        runs = [solve(w, verbose=True)]

    else:
        runs = run_batch(args.batch_size, verbose=args.verbose)

    report_stats(runs)


if __name__ == '__main__':
    main()






