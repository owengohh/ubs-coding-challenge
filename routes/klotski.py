import collections
import json
import logging

from flask import request

from routes import app

logger = logging.getLogger(__name__)


@app.route('/klotski', methods=['POST'])
def evaluate():
    data = request.get_json()
    logging.info("data sent for evaluation {}".format(data))
    res = []
    for item in data:
        logger.info("item sent for evaluation {}".format(item))
        board = item.get("board")
        moves = item.get("moves")
        result = klotski(board, moves)
        res.append(result)
    return json.dumps(res)


def klotski(board, moves):
    directions = {
        "W": (0, -1),
        "N": (-1, 0),
        "E": (0, 1),
        "S": (1, 0)
    }
    board_list = []
    for i in range(0, len(board), 4):
        board_list.append(list(board[i:i+4]))
    moves_list = []
    for i in range(0, len(moves), 2):
        moves_list.append(moves[i:i+2])
    ch_positions = collections.defaultdict(list)

    for i in range(len(board_list)):
        for j in range(len(board_list[i])):
            if board_list[i][j] != "@":
                ch_positions[board_list[i][j]].append((i, j))

    for move in moves_list:
        ch, direction = move[0], move[1]
        # move all the positions by the direction in the ch_positions
        updated_positions = []
        for pos in ch_positions[ch]:
            x, y = pos
            dx, dy = directions[direction]
            nx, ny = x + dx, y + dy
            if nx < 0 or nx >= len(board_list) or ny < 0 or ny >= len(board_list[0]):
                "print('Invalid move')"
                break
            updated_positions.append((nx, ny))
        ch_positions[ch] = updated_positions

    # form the updated board
    updated_board = [["@" for _ in range(len(board_list[0]))]
                     for _ in range(len(board_list))]
    for ch, positions in ch_positions.items():
        for pos in positions:
            x, y = pos
            updated_board[x][y] = ch
    return "".join(["".join(row) for row in updated_board])
