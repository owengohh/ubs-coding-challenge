import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)


@app.route('/the-clumsy-programmer', methods=['POST'])
def eval_clumsy_programmer():
    data = request.get_json()
    res = []
    for item in data[:4]:
        dictionary = item.get("dictionary")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dictionary, mistypes)
        res.append(result)
    return json.dumps(res)


def one_char_difference(word1, word2):
    if len(word1) != len(word2):
        return False
    differences = sum(1 for a, b in zip(word1, word2) if a != b)
    return differences == 1


def find_closest_word(word, dict):
    for candidate in dict:
        if one_char_difference(word, candidate):
            return candidate
    return word


def clumsy_programmer(dict, mistypes):
    dict_set = set(dict)
    corrected_words = []
    for word in mistypes:
        corrected_word = find_closest_word(word, dict_set)
        corrected_words.append(corrected_word)
    return {
        "corrections": corrected_words
    }
