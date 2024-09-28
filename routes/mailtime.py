import collections
from datetime import datetime
import json
import logging

from flask import request
from routes import app

logger = logging.getLogger(__name__)

class Email:
    def __init__(self, email_json):
        self.subject = email_json["subject"].split("RE: ")[-1]
        self.time = int(datetime.fromisoformat(email_json["timeSent"]).timestamp())
        self.sender = email_json["sender"]
        self.receiver = email_json["receiver"]

@app.route('/mailtime', methods=['POST'])
def eval_mailtime():
    graph = collections.defaultdict(list)
    people = collections.defaultdict(list)

    def solve(request_json):
        for email in request_json["emails"]:
            new_email = Email(email)
            graph[new_email.subject].append(new_email)
        
        for subject in graph:
            graph[subject].sort(key = lambda x:x.time)
            for i in range(1, len(graph[subject])):
                responder_email = graph[subject][i]
                people[responder_email.sender].append(responder_email.time - graph[subject][i-1].time)

        result = {}
        for person_obj in request_json["users"]:
            person = person_obj["name"]
            if len(people[person]) == 0:
                result[person] = 0
            else:
                result[person] = sum(people[person])//len(people[person])

        return {"response": result}

    return json.dumps(solve(request.get_json()))
