import Levenshtein
import json
import logging

from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/the-clumsy-programmer', methods=['POST'])
def eval_clumsy_programmer():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    res = []
    for item in data:
        logger.info("item sent for evaluation {}".format(item))
        dictionary = item.get("dict")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dict, mistypes)
        res.append(result)
    return jsonify(res)


def clumsy_programmer(dictionary, mistypes):
    corrected_words = []
    for word in mistypes:
        closest_word = min(dict, key=lambda w: Levenshtein.distance(word, w))
        corrected_words.append(closest_word)
    return {
        "corrections": corrected_words
    }
