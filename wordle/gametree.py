from typing import List, Tuple, Dict
from wordle import HIT, CLOSE, MISS
import words
from math import log, inf

def get_hint_for_word_from_guess(target_word, guess):
    result = []
    for (tc, gc) in zip(target_word, guess):
        if tc == gc:
            result.append(HIT)
        elif gc in target_word:
            result.append(CLOSE)
        else:
            result.append(MISS)
    return tuple(result)

def entropy(xs, base=None):
    total = sum(xs)
    ps = [l / total for l in xs]
    if base is None:
        H = -1 * sum([p * log(p) for p in ps])
    else:
        H = -1 * sum([p * log(p)/log(base) for p in ps])
    return H


def entropy_of_wordsets(wordsets, base=None):
    return entropy([len(ws) for ws in wordsets], base=base)

class Node:
    def __init__(self, remaining_words=None, depth=0):
        self.remaining_words = remaining_words
        if remaining_words is None:
            self.remaining_words = words.get_words()
        self.depth=depth
        self.children = {}

    def apply_guess_to_remaining_words(self, guess):
        hints_to_wordset = {}
        for w in self.remaining_words:
            hint = get_hint_for_word_from_guess(w, guess)
            hints_to_wordset.setdefault(hint, [])
            hints_to_wordset[hint].append(w)
        return hints_to_wordset

        
    def compute_guess_entropies(self, guesses=None) -> List[Tuple[str, float]]:
        if guesses is None:
            guesses = words.get_words()
        # Find max entropy wordset
        result = []
        for guess in guesses:
            hints_to_wordset = self.apply_guess_to_remaining_words(guess)
            wordsets = list(hints_to_wordset.values())
            H = entropy_of_wordsets(wordsets)
            result.append((guess, H))
        
        return result

    def max_entropy_guesses(self, n=1) -> List[Tuple[str, float]]:
        entropy_guesses = self.compute_guess_entropies()
        entropy_guesses.sort(key=lambda x: x[1], reverse=True)
        return entropy_guesses[:n]
    
    def make_max_entropy_guesses(self, n=1):
        guesses_and_entropies = self.max_entropy_guesses(n=n)
        for (guess, _) in guesses_and_entropies:
            self.play(guess)
        return guesses_and_entropies

    def play(self, guess) -> Dict[Tuple[int], 'Node']:
        new_depth = self.depth + 1
        hints_to_wordsets = self.apply_guess_to_remaining_words(guess)
        hints_to_nodes = {h: Node(ws, new_depth) for (h, ws) in hints_to_wordsets.items()}
        self.children[guess] = hints_to_nodes
        return self.children[guess]

    def populate(self, up_to_depth=6, debug_up_to_depth=1):
        start = '   ' * self.depth
        debug=self.depth <= debug_up_to_depth
        if debug:
            print(f"{start}Populating node (depth={self.depth}) with {len(self)} words")
        if self.depth >= up_to_depth:
            return
        if len(self.children) == 0:
            self.make_max_entropy_guesses(n=1)

        for (guess, hints_to_nodes) in self.children.items():
            if debug:
                print(f"{start}guess={guess}")
            num_nodes = len(hints_to_nodes)
            for i, node in enumerate(hints_to_nodes.values()):
                if debug:
                    print(f"{start}node {i} of {num_nodes}")
                node.populate()
        
    def __len__(self):
        return len(self.remaining_words)

    def __getitem__(self, x):
        return self.children[x]

    def __str__(self):
        return f""
            

