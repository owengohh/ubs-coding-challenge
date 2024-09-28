import Levenshtein
import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

@app.route('/the-clumsy-programmer', methods=['POST'])
def eval_clumsy_programmer():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    res = []
    for item in data:
        logger.info("item sent for evaluation {}".format(item))
        dict = item.get("dict")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dict, mistypes)
        res.append(result)
    return json.dumps(res)

def clumsy_programmer(dict, mistypes):
    corrected_words = []
    for word in mistypes:
        closest_word = min(dict, key=lambda w: Levenshtein.distance(word, w))
        corrected_words.append(closest_word)
    return corrected_words
