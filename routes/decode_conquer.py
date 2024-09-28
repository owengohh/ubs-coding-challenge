import json
import logging

from flask import request, jsonify

from routes import app

logger = logging.getLogger(__name__)


@app.route('/ub5-flags', methods=['GET'])
def eval_ub5_flags():
    return jsonify({
        "sanityScroll": {
            "flag": "UB5{w3lc0m3_70_c7f_N0ttyB01}"
        },
        "openAiExploration": {
            "flag": "FLAG_CONTENT_HERE"
        },
        "dictionaryAttack": {
            "flag": "UB5{FLAG_CONTENT_HERE}",
            "password": "PASSWORD_HERE"
        },
        "pictureSteganography": {
            "flagOne": "UB5-1{1_am_d3f_n0t_old}",
            "flagTwo": "UB5-2{1amlik3n3w}"
        },
        "reverseEngineeringTheDeal": {
            "flag": "FLAG_CONTENT_HERE",
            "key": "KEY_HERE"
        }
    })
