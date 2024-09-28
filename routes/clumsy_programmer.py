import difflib
import logging

from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/the-clumsy-programmer', methods=['POST'])
def eval_clumsy_programmer():
    data = request.get_json()
    res = []
    for item in data:
        dictionary = item.get("dictionary")
        mistypes = item.get("mistypes")
        result = clumsy_programmer(dictionary, mistypes)
        res.append(result)
    return jsonify(res)


def clumsy_programmer(dict, mistypes):
    corrected_words = []
    for word in mistypes:
        # Find the closest match using difflib
        closest_matches = difflib.get_close_matches(
            word, dict, n=1, cutoff=0.0)
        if closest_matches:
            corrected_words.append(closest_matches[0])
        else:
            # If no close match is found, keep the original word
            corrected_words.append(word)
    return {
        "corrections": corrected_words
    }
