import json
import logging

from flask import request
from routes import app

logger = logging.getLogger(__name__)

@app.route('/coolcodehack', methods=['POST'])
def eval_coolcodehack():
    return json.dumps({
        "username": "hello",
        "password": "world"
    })