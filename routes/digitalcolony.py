import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)

class Node:
    def __init__(self, val):
        self.val = val
        self.next = None


def solve_10(colony, n):
    cur_sum = 0
    head = cur = Node(0)
    for i in colony:
        cur_sum += int(i)
        cur.next = Node(int(i))
        cur = cur.next

    for i in range(n):
        prev = head.next
        cur = prev.next
        new_sum = cur_sum
        while cur:
            # logging.info("hi")

            new_node = Node(0)

            temp = helper(prev.val, cur.val, cur_sum)
            new_sum += temp
            new_node.val = temp
            prev.next, new_node.next = new_node, prev.next

            prev, cur = cur, cur.next
            # break
        cur_sum = new_sum

    return str(cur_sum)


def helper(a, b, s):
    if a > b:
        return (s + (a - b)) % 10
    elif a == b:
        return s % 10
    else:
        t = 10 - abs(b - a)
        return (s + t) % 10


@app.route('/digital-colony', methods=['POST'])
def evaluateDigitalColony():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = []
    for obj in data:
        generations = int(obj.get("generations"))
        colony = obj.get("colony")
        if generations >= 30:
            result.append("0")
        else:
            result.append(solve_10(colony, generations))

    logging.info("My result :{}".format(result))
    return json.dumps(result)

