import logging
from flask import request, jsonify
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
    return jsonify(res)


def preprocess_dictionary(dictionary):
    pattern_to_words = {}
    for word in dictionary:
        word = word.strip()
        for i in range(len(word)):
            # Create a pattern by replacing the character at position i with '_'
            pattern = word[:i] + '_' + word[i+1:]
            pattern_to_words.setdefault(pattern, set()).add(word)
    return pattern_to_words


def find_closest_word(word, pattern_to_words):
    for i in range(len(word)):
        # Generate a pattern by replacing the character at position i with '_'
        pattern = word[:i] + '_' + word[i+1:]
        if pattern in pattern_to_words:
            # Exclude the word itself from the candidates
            candidates = pattern_to_words[pattern] - {word}
            if candidates:
                # Return the first candidate (you can modify this to select the best one if needed)
                return next(iter(candidates))
    return word  # Return the original word if no correction is found


def clumsy_programmer(dictionary, mistypes):
    pattern_to_words = preprocess_dictionary(dictionary)
    corrected_words = []
    for word in mistypes:
        corrected_word = find_closest_word(word, pattern_to_words)
        corrected_words.append(corrected_word)
    return {
        "corrections": corrected_words
    }
