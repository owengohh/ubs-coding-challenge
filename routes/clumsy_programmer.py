import Levenshtein
import logging

from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/the-clumsy-programmer', methods=['POST'])
def eval_clumsy_programmer():
    data = request.get_json()
    res = []
    for item in data[:4]:
        logger.info("item sent for evaluation {}".format(item))
        dictionary = item.get("dictionary")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dictionary, mistypes)
        res.append(result)
    return jsonify(res)


def clumsy_programmer(dictionary, mistypes):
    corrected_words = []
    for word in mistypes:
        closest_word = min(
            dictionary, key=lambda w, current_word=word: Levenshtein.distance(current_word, w))
        corrected_words.append(closest_word)
    return {
        "corrections": corrected_words
    }
