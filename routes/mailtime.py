import collections
from datetime import datetime
import json
import logging

from flask import request
from routes import app

logger = logging.getLogger(__name__)


@app.route('/mailtime', methods=['POST'])
def eval_mailtime():
    graph = collections.defaultdict(list)
    people = collections.defaultdict(list)

    def solve(request_json):
        for email in request_json["emails"]:
            subject = email["subject"].split("RE: ")[-1]
            graph[subject].append(
                int(datetime.fromisoformat(email["timeSent"]).timestamp())
            )
            if len(graph[subject]) > 1:
                people[email["sender"]].append(
                    graph[subject][-1] - graph[subject][-2])

        result = {}
        for person in people:
            result[person] = sum(people[person]) // len(people[person])
        return result

    return json.dumps({
        "response": solve(request.get_json())
    })
