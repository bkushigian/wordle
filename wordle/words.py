import random

_WORDS = []
with open("../words") as f:
    _WORDS = [w.strip() for w in f.readlines()]
    _WORDS = [w for w in _WORDS if len(w) == 5]


def get_words():
    return list(_WORDS)


def get_random_word():
    return random.choice(_WORDS)


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
