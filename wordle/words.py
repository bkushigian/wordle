import random
from string import ascii_lowercase


def get_words():
    return list(_WORDS)


def get_random_word():
    return random.choice(_WORDS)


def is_valid_word(word):
    return word in _WORDS_SET


def word_contains_all_letters(word, letters):
    """
    Test to see if this word contains all letters in iterable 'letters'
    :param word: the word we wish to test
    :param letters: the letters we want to test for inclusion
    :return:
    """
    word_s = set(word)
    for let in letters:
        if let not in word_s:
            return False
    return True


def word_omits_all_letters(word, letters):
    """
    Test to see if this word omits all letters in iterable 'letters'
    :param word: the word we wish to test
    :param letters: the letters we want to test for omission
    :return:
    """
    word_s = set(word)
    for let in letters:
        if let in word_s:
            return False
    return True


def omit_letters(letters, ws=None):
    """
    Return a list of words which contain none of the provided letters
    :param letters:
    :param ws:
    :return:
    """
    if ws is None:
        ws = get_words()
    return [w for w in ws if word_omits_all_letters(w, letters)]


def _word_has_letters_at_positions(word, positions):
    for (let, pos) in positions:
        if not (0 <= pos < len(word)) or word[pos] != let:
            return False
    return True


def with_letters_at_positions(positions, ws=None):
    if ws is None:
        ws = get_words()
    return [w for w in ws if _word_has_letters_at_positions(w, positions)]


def _word_has_letters_not_at_positions(word, positions):
    for (let, pos) in positions:
        if let not in word or (0 <= pos < len(word) and word[pos] == let):
            return False
    return True


def with_letters_not_at_positions(positions, ws=None):
    if ws is None:
        ws = get_words()
    return [w for w in ws if _word_has_letters_not_at_positions(w, positions)]


def get_letter_frequencies(ws=None, verbose=False):
    if ws is None:
        ws = get_words()
    freqs = {let: len([w for w in ws if let in w]) for let in ascii_lowercase}
    if verbose:
        for let in ascii_lowercase:
            print(f"{let}: {freqs[let]:6}  ({100 * freqs[let] / len(ws)}%)")
    return freqs


def score_word_by_freqs(word, freqs=None):
    if freqs is None:
        freqs = get_letter_frequencies(get_words())
    return sum(freqs[l] for l in set(word))


def score_words_by_freqs(words=None):
    if words is None:
        words = get_words()
    frqs = get_letter_frequencies(ws=words)
    return {word: score_word_by_freqs(word, frqs) for word in words}


def get_max_word_by_freqs(words=None):
    if words is None:
        words = get_words()
    scores = score_words_by_freqs(words)
    best_word = 'EMPTY'
    best_score = 0
    for word, score in scores.items():
        if score > best_score:
            best_word, best_score = word, score

    return best_word, best_score


def get_top_n_words_by_freqs(words=None, n=5):
    scores = sorted(list(score_words_by_freqs(words=words).items()), key=lambda t: t[1], reverse=True)
    return scores[:n]


letter_set = set(ascii_lowercase)
_WORDS = []
_WORDS_SET = set()
with open("../wordfiles/words") as f:
    _WORDS = [w.strip() for w in f.readlines()]
    _WORDS = [w for w in _WORDS if len(w) == 5]
    _WORDS = omit_letters("ABCDEFGHIJKLMNOPQRSTUVWXYZ", _WORDS)
    _WORDS = [w for w in _WORDS if set(w).issubset(letter_set)]

    with open("../wordfiles/words2", 'w+') as f:
        f.write('\n'.join(_WORDS))
    _WORDS_SET = set(_WORDS)
