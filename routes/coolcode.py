import logging

from flask import request, jsonify
from routes import app

logger = logging.getLogger(__name__)

@app.route('/coolcodehack', methods=['POST'])
def eval_coolcodehack():
    return jsonify({
        "username": "tester12345",
        "password": "Password123!"
    })