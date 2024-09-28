import os
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


def process_chunk(chunk, dict_set):
    return [find_closest_word(word, dict_set) for word in chunk]


def clumsy_programmer(dict, mistypes):
    dict_set = set(dict)
    corrected_words = []
    num_threads = min(32, os.cpu_count() + 4)
    chunk_size = max(1, len(mistypes) // num_threads)
    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for i in range(0, len(mistypes), chunk_size):
            chunk = mistypes[i:i + chunk_size]
            futures.append(executor.submit(process_chunk, chunk, dict_set))

        for future in as_completed(futures):
            try:
                corrected_words.extend(future.result())
            except Exception as e:
                print(f"Error processing chunk: {e}")
    return {
        "corrections": corrected_words
    }
