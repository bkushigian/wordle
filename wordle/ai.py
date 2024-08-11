from words import *
from wordle import Wordle, HIT, CLOSE, MISS
import gametree as gt
from cli import print_guess_result
from statistics import mean, median, mode
from argparse import ArgumentParser
from random import choice
import multiprocessing


def next_guess(ws, top=1):
    choices = get_top_n_words_by_freqs(ws, top)
    return choice(choices)[0]


def apply_hint(guess, hint, ws):
    misses = []
    closes = []
    hits = []
    for i, (letter, status) in enumerate(zip(guess,hint)):
        if status == MISS:
            misses.append(letter)
        elif status == HIT:
            hits.append((letter, i))
        elif status == CLOSE:
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
                print(f"    {print_guess_result(g, hint)}")
            ws = apply_hint(g, hint, ws)
        except RuntimeError as e:
            print(str(e))

    if not w.game_won:
        print(f"Lost game: {w.word} with {len(w.guesses)} guesses")
    return len(w.guesses), w.game_won


def solve_with_max_entropy(w: Wordle, first_words=None, n=1, verbose=False):
    """
    The main AI for wordle, this succeeds for over 99% of test words.

    This function computes for each possible guess `g` and each possible
    remaining word `w` what hint the guess would produce if that word were the
    target word. It uses this to collect potential target words into wordsets,
    and associates each possible hint with the wordset of words that would give
    the particular hint given the guess.

    """
    path = []
    if first_words is None:
        first_words = ["tares"]
    elif first_words == '':
        first_words = []
    root = gt.Node()
    node = root
    path.append(('', (0, 0, 0, 0, 0), node))
    if verbose:
        print(f"First words={first_words}")
    for guess in first_words:
        if verbose:
            print(f"- {len(node)} words remaining")
            print(f"  - Applying predefined guess {guess}")
        try:
            hint = w.guess(guess)
        except RuntimeError as e:
            raise e

        if verbose:
            print(f"  - Got hint {hint}")
        node = node.play(guess)[hint]
        path.append((guess, hint, node))
        if not w.is_running():
            return len(w.guesses), w.game_won, path
    
    if verbose:
        print("(Solving with max entropies words...)")
    while node.depth < 6:
        if verbose:
            print(f"- {len(node)} words remaining")

        if len(node) == 0:
            raise RuntimeError("No more guesses")
        if len(node) == 1:
            g = node.remaining_words[0]
            if verbose:
                print(f"  - Applying only remaining guess '{g}'")
        else:
            if verbose:
                print(f"  - Computing guesses with max entropies...'")
            max_entropy_guesses = node.max_entropy_guesses(n=n)
            if verbose:
                print(f"  - Potential guesses: {', '.join([f'{_g}: {_h:4.2f}' for _g, _h in max_entropy_guesses])}")
            (g, h) = random.choice(max_entropy_guesses)
            if verbose:
                print(f"  - Applying max entropy guess '{g}' (H={h:4.2})")
        hint = w.guess(g)
        try:
            node = node.play(g)[hint]
        except KeyError as e:
            print(f"Error: node with {len(node)} remaining words")
            print(f"Unrecognized key: {hint}")
            print(f"Valid keys: {hint}")

            raise e
        path.append((g, hint, node))
        if not w.is_running():
            return len(w.guesses), w.game_won, path

    return len(w.guesses), w.game_won, path

def solve_with_max_frequencies(w: Wordle, verbose=False):
    """
    Outdated AI for wordle, this computes the frequencies of letters and then
    choses the word that has the highest frequency score (so an e counts more
    than a z).

    This is not good and should not be used :)
    """
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
            ws = apply_hint(g, hint, ws)
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


def interactive(first_words=None, n=1):
    if first_words is None:
        first_words = ['tares']
    root = gt.Node()
    node = root

    codes = {'G': HIT, 'g': HIT,
                'Y': CLOSE, 'y': CLOSE,
                'B': MISS, 'b': MISS}

    i = 0
    while True:
        i += 1
        print(f"--- Round {i}: {len(node)} words remaining ---")
        if len(node) < 100:
            words_to_print = list(node.remaining_words)
            while len(words_to_print) > 0:
                row, words_to_print = words_to_print[:10], words_to_print[10:]
                print("   \033[32;1;3m", (' '.join(row).upper()), "\033[0m")

        if len(first_words) > 0:
            suggestions = [first_words[0]]
            first_words = first_words[1:]
        elif len(node) == 1:
            suggestions = list(node.remaining_words)
        else:
            max_h_guesses = node.max_entropy_guesses(n=n)
            suggestions = [x[0] for x in max_h_guesses]
        print(f"\033[34;1mSuggestions\033[0m: {' '.join(suggestions)} ")

        invalid_input = True
        while invalid_input:
            invalid_input = False
            g = input(f"(\033[34;1mEnter Guess\033[0m)> ")
            g2 = g.strip().replace(' ', '')
            if len(g2) != 5:
                invalid_input = True
                print(f"    \033[31mInvalid guess:\033[0m {g}")
            if not is_valid_word(g2):
                invalid_input = True
                print(f"    \033[31mInvalid guess: not in words list:\033[0m {g}")
        try:
            hint = None
            invalid_input = True
            while invalid_input:
                invalid_input = False
                hint = []
                feedback = input("(\033[34;1mEnter Feedback [? for help]\033[0m)> ").strip()
                if feedback == '?':
                    print("For each letter in your guess, write:\n"
                          " - 'G' if it was \033[32;1mgreen\033[0m,\n"
                          " - 'Y' if it was \033[33;1myellow\033[0m, and\n"
                          " - 'B' if it was \033[1mblack\033[0m")
                    invalid_input = True
                elif len(feedback) == 5:
                    for fb, let in zip(feedback, g):
                        if fb not in codes:
                            print(f"Invalid feedback character: {fb}")
                            invalid_input = True
                            break
                        hint.append(codes[fb])
                    hint = tuple(hint)
                else:
                    print("Invalid feedback: length must be 5")
                    invalid_input = True

            print(f"    {print_guess_result(g, hint)}")
            node = node.play(g)[hint]

        except RuntimeError as e:
            print(str(e))


def report_stats(runs):
    no_runs = len(runs)
    wins = [run for run in runs if run[2]]
    losses = [run for run in runs if not run[2]]
    no_wins = len(wins)
    no_losses = len(losses)
    n_guesses = [run[1] for run in runs]
    mean_guesses_in_wins = mean(n_guesses)
    mode_guesses_in_wins = mode(n_guesses)
    median_guesses_in_wins = median(n_guesses)

    print("Lost on the following words:")
    for (word, guesses, w, path) in losses:
        print("    ", word)
    print(f"Runs: {no_runs}")
    print(f"Wins: {no_wins} ({100 * no_wins / no_runs}%)    Losses: {no_losses} ({100 * no_losses / no_runs}%)")
    print(f"Num Guesses")
    print(f"    Min:    {min(n_guesses)}")
    print(f"    Max:    {max(n_guesses)}")
    print(f"    Mean:   {mean_guesses_in_wins}")
    print(f"    Median: {median_guesses_in_wins}")
    print(f"    Mode:   {mode_guesses_in_wins}")


def main():
    parser = ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Print intermediate run information")
    parser.add_argument("--word", default=None, help="Set Wordle word to try to solve. This results in a single run")
    parser.add_argument("-s", "--batch_size", default=500, type=int, help="Batch size for running stats")
    parser.add_argument("-i", "--interactive", action="store_true", help="Run an interactive session")
    parser.add_argument("-n", "--num_choices", type=int, default=1, help="Number of choices to consider at each step")
    parser.add_argument("-b", "--batches", action='store_true', help="Run batches")

    args = parser.parse_args()
    if args.interactive:
        interactive(n=args.num_choices)
        return
    elif args.batches:
        runs = []
        for i in range(args.batch_size):
            print(f"[[[\033[32;1mBatch {i+1} of {args.batch_size}\033[0m]]]")
            runs.append(test(word=args.word, n=args.num_choices, verbose=args.verbose, print_summary=False))
        report_stats(runs)

    else:
        test(word=args.word, verbose=args.verbose)

def test(word=None, first_words=None, n=1, verbose=False, print_summary=True, remaining_words_print_threshold=100):
    if word is None:
        print("  Choosing random word...")
        word = get_random_word()
    print(f"  + \033[1mWord To Guess\033[0m: \033[94;1m{word.upper()}\033[0m")
    w = Wordle(word)
    n_guesses, won, path = solve_with_max_entropy(w, first_words=first_words, n=n, verbose=verbose)
    if won:
        print(f"  + \033[32;1mWon\033[0;1m with {n_guesses} guesses\033[0m")
    else:
        print(f"  + \033[31;1mLost with {n_guesses} guesses\033[0m")
        
    root = path[0][2]
    if print_summary:
        print(f"    (\033[1mBeginning With \033[35;1m{len(root):5}\033[1m Words\033[0m)")
        for guess_no, (guess, hint, n) in enumerate(path[1:]):
            colored_guess = print_guess_result(guess, hint)
            print(f"    [\033[32;1m{guess_no + 1}\033[0m] \033[1mGuessed\033[0m {colored_guess}: {len(n):5} Words Remaining")
            if len(n) < remaining_words_print_threshold:
                words_to_print = list(n.remaining_words)
                while len(words_to_print) > 0:
                    row, words_to_print = words_to_print[:10], words_to_print[10:]
                    print("       \033[32;1;3m", (' '.join(row).upper()), "\033[0m")
    return word, len(w.guesses), w.game_won, path
    
if __name__ == '__main__':
    main()

