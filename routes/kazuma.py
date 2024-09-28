import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)


@app.route('/efficient-hunter-kazuma', methods=['POST'])
def eval_kazuma():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    res = []
    for item in data:
        logger.info("item sent for evaluation {}".format(item))
        monsters = item.get("monsters")
        result = kazuma(monsters)
        res.append(result)
    return json.dumps(res)


def kazuma(monsters):
    dp = [0] * len(monsters)
    for i in range(1, len(monsters)):
        for prev in range(i - 1, -1, -1):
            gain = monsters[i] - monsters[prev] + \
                (dp[prev - 2] if prev - 2 >= 0 else 0)
            print(i, prev, gain, dp[prev - 2] if prev - 2 >= 0 else 0)
            dp[i] = max(dp[i-1], gain, dp[i])
    return {"efficiency": dp[-1]}
