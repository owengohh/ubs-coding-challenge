from rapidfuzz import process
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
        logging.info("item sent for evaluation {}".format(item))
        dictionary = item.get("dictionary")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dictionary, mistypes)
        res.append(result)
    return json.dumps(res)


def clumsy_programmer(dictionary, mistypes):
    corrected_words = []
    for word in mistypes:
        closest_word = process.extractOne(word, dictionary)[0]
        corrected_words.append(closest_word)
    return {
        "corrections": corrected_words
    }
