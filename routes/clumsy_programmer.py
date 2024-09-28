import Levenshtein
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
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


def find_closest_word(word, dict):
    return min(dict, key=lambda w: Levenshtein.distance(word, w))


def clumsy_programmer(dict, mistypes):
    corrected_words = []
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(
            find_closest_word, word, dict): word for word in mistypes}
        for future in as_completed(futures):
            try:
                closest_word = future.result()
                corrected_words.append(closest_word)
            except Exception as e:
                print(f"Error processing word {futures[future]}: {e}")
    return {
        "corrections": corrected_words
    }
