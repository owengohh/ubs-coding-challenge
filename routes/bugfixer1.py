import json
import logging

from flask import request

from routes import app
from collections import deque

logger = logging.getLogger(__name__)

def calculate_min_time(time_list, prerequisites):
    n = len(time_list)
    if n == 0:
        return 0
    projects = [i + 1 for i in range(n)]
    duration = {i + 1: time_list[i] for i in range(n)}  # Map project number to its duration

    indegrees = {i + 1: 0 for i in range(n)}
    graph = {i + 1: [] for i in range(n)}

    for a, b in prerequisites:
        graph[a].append(b)
        indegrees[b] += 1

    earliest_start = {i + 1: 0 for i in range(n)}
    earliest_finish = {i + 1: 0 for i in range(n)}

    queue = deque([project for project in projects if indegrees[project] == 0])

    # toposort algo
    while queue:
        project = queue.popleft()
        earliest_finish[project] = earliest_start[project] + duration[project]

        for preReq in graph[project]:
            earliest_start[preReq] = max(earliest_start[preReq], earliest_finish[project])
            indegrees[preReq] -= 1
            if indegrees[preReq] == 0:
                queue.append(preReq)

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
