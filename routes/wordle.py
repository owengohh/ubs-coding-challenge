import re
from collections import Counter
import requests
import json
# get list of five-letter words from meaningpedia.com
meaningpedia_resp = requests.get(
    "https://meaningpedia.com/5-letter-words?show=all")

# compile regex
pattern = re.compile(r'<span itemprop="name">(\w+)</span>')
# find all matches
word_list = pattern.findall(meaningpedia_resp.text)


@app.route('/wordle-game', methods=['POST'])
def eval_wordle():
    data = request.get_json()
    guess_history = data.get("guessHistory")
    evaluation_history = data.get("evaluationHistory")
    result = get_next_best_guess(word_list, guess_history, evaluation_history)
    return json.dumps(result)


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

    # Step 4: Select Best Guess
    best_guess = max(word_scores, key=word_scores.get)
    return best_guess


