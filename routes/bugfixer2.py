import json
import logging
import heapq

from flask import request

from routes import app
from collections import deque

logger = logging.getLogger(__name__)

@app.route('/bugfixer/p2', methods=['POST'])
def bugfixer_p2():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    result = []
    for obj in data:
        bugseq = list(obj.get("bugseq"))
        # bugseq[ i ] = [Difficultyi , Limiti]
        # greedy by limit
        logging.info("bugseq {}".format(bugseq))
        bugSeqSortedByLimit = sorted(bugseq, key=lambda x:x[1])

        #  use a max heap to maintain the order of bugs at each iteration
        maxHeap = []
        totalTime = 0
        for difficulty, limit in bugSeqSortedByLimit:
            totalTime += difficulty # maintains the positive total time
            heapq.heappush(maxHeap, -1 * difficulty)
            if totalTime > limit:
                toRemove = -1 * heapq.heappop(maxHeap)
                totalTime -= toRemove
            logging.info("maxHeap:" + str(maxHeap))
        result.append(len(maxHeap))

    logging.info("My result :{}".format(result))
    return json.dumps(result)
