import re
from collections import Counter
import requests
import json
from flask import request, jsonify

from routes import app
import logging

logger = logging.getLogger(__name__)

@app.route('/wordle-game', methods=['POST'])
def eval_wordle():
    with open('./data/words.txt', 'r') as file:
        word_list = [line.strip() for line in file if len(line.strip()) == 5]
    data = request.get_json()
    guess_history = data.get("guessHistory")
    evaluation_history = data.get("evaluationHistory")
    result = get_next_best_guess(word_list, guess_history, evaluation_history)
    return jsonify({"guess": result})


def get_next_best_guess(word_list, guess_history, evaluation_history):
    # Step 1: Parse Evaluations
    confirmed_positions = {}
    present_letters = set()
    absent_letters = set()
    excluded_positions = {}

    for guess, evaluation in zip(guess_history, evaluation_history):
        for index, (letter, symbol) in enumerate(zip(guess, evaluation)):
            if symbol == 'O':
                confirmed_positions[index] = letter
            elif symbol == 'X':
                present_letters.add(letter)
                excluded_positions.setdefault(letter, set()).add(index)
            elif symbol == '-':
                absent_letters.add(letter)
            # Handle '?' if necessary

    # Step 2: Filter Possible Words
    possible_words = []
    for word in word_list:
        if len(word) != 5:
            continue
        match = True
        # Check confirmed positions
        for index, letter in confirmed_positions.items():
            if word[index] != letter:
                match = False
                break
        if not match:
            continue
        # Check absent letters
        if any(letter in word for letter in absent_letters):
            continue
        # Check present letters and their positions
        for letter in present_letters:
            if letter not in word:
                match = False
                break
            if any(word[index] == letter for index in excluded_positions.get(letter, [])):
                match = False
                break
        if match:
            possible_words.append(word)

    letter_frequencies = Counter()
    for word in possible_words:
        letter_frequencies.update(set(word))
    word_scores = {}
    for word in possible_words:
        score = sum(letter_frequencies[letter] for letter in set(word))
        word_scores[word] = score

    logging.info(f"Word scores: {word_scores}")
    # Step 4: Select Best Guess
    best_guess = max(word_scores, key=word_scores.get)
    return best_guess
