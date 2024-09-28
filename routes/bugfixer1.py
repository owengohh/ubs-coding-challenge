import json
import logging

from flask import request

from routes import app
from collections import deque

logger = logging.getLogger(__name__)

def calculate_min_time(time_list, prerequisites):
    n = len(time_list)
    projects = [i+1 for i in range(n)]
    duration = {i+1: time_list[i] for i in range(n)}  # Map project number to its duration

    in_degree = {i+1: 0 for i in range(n)}
    adj = {i+1: [] for i in range(n)}

    for a, b in prerequisites:
        adj[a].append(b)
        in_degree[b] += 1

    earliest_start = {i+1: 0 for i in range(n)}
    earliest_finish = {i+1: 0 for i in range(n)}

    queue = deque([u for u in projects if in_degree[u] == 0])
    # queue = deque(queue)

    # toposort algo
    while queue:
        u = queue.popleft()
        earliest_finish[u] = earliest_start[u] + duration[u]

        for v in adj[u]:
            earliest_start[v] = max(earliest_start[v], earliest_finish[u])
            in_degree[v] -= 1
            if in_degree[v] == 0:
                queue.append(v)

    total_time = max(earliest_finish.values())

    return total_time

@app.route('/bugfixer/p1', methods=['POST'])
def bugfixer_p1():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = []
    for obj in data:
        time = obj['time']
        prerequisites = obj['prerequisites']

        total_time = calculate_min_time(time, prerequisites)
        result.append(total_time)

    # result = None
    logging.info("My result :{}".format(result))
    return json.dumps(result)

import json
from flask import Flask, request

app = Flask(__name__)

