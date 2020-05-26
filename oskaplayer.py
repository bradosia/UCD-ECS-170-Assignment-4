# Assignment 4
# Student: Branden Lee

# oskaplayer.py
# some examples:
# oskaplayer(['wwww','---','--','---','bbbb'],'w',2)
# oskaplayer(['-----','--wb','-b-','--','-w-','bbbb','-b---'],'b',2)
# oskaplayer(['-----','--wb','-b-','--','-w-','bbbb','-b---'],'w',2)

# Note: The first line of the array is 'w' side and the last line is 'b' side.
# 'w' can only move towards 'b' side and 'b' can only move towards 'w' side

import math


# oskaplayer outputs the best next move that the designated player
# can make from that given board position.
# @param start_state_array 2n - 3 strings representing starting state
# @param side character 'b' or 'w', which side to play
# @param depth Max moves to look ahead
# @return array of rows representing board for best move using minimax algorithm
# @return None if no move possible
def oskaplayer(start_state_array, side, depth):
    # width = widest row size
    width = validate_board(start_state_array)
    if width is None:
        print("Start state is invalid!")
    elif side != 'w' and side != 'b':
        print("Side is invalid! must be 'w' or 'b'.")
    elif type(depth) != int and depth > 0:
        print("Depth is invalid! must be an integer greater than 0.")
    else:
        start_state = State()
        start_state.id = serialize(start_state_array)
        start_state.side = side
        start_state.g = 0
        return_state = minimax_search(start_state, side, True, depth)
        if return_state is None:
            print("No next best move found.")
            return None
        else:
            return_state_array = unserialize(return_state.id)
            return return_state_array


# MiniMax search implemented recursively
# @param current_state current state object
# @param side character 'b' or 'w', which side to play
# @param depth initial max moves to look ahead
# @return the best state object given the initial state object
def minimax_search(current_state, side, side_flag, depth):
    if side == 'b':
        opponent = 'w'
    else:
        opponent = 'b'
    if current_state.g == depth:
        current_state.h = calculate_heuristic(current_state.id, side)
        return current_state
    if side_flag:
        return_state = State()
        return_state.h = -9999
        state_array = unserialize(current_state.id)
        new_state_list = movegen(state_array, side)
        n = len(new_state_list)
        for i in range(0, n):
            child_state = State()
            child_state.id = new_state_list[i]
            child_state.g = current_state.g + 1
            child_state = minimax_search(child_state, opponent, False, depth)
            return_state = max(return_state, child_state)
        # only first depth level returns new moves
        if current_state.g == 0:
            return return_state
        # other depths just pass up the heuristic value
        current_state.h = return_state.h
        return current_state
    if not side_flag:
        return_state = State()
        return_state.h = 9999
        state_array = unserialize(current_state.id)
        new_state_list = movegen(state_array, side)
        n = len(new_state_list)
        for i in range(0, n):
            child_state = State()
            child_state.id = new_state_list[i]
            child_state.g = current_state.g + 1
            child_state = minimax_search(child_state, opponent, True, depth)
            return_state = min(return_state, child_state)
            current_state.h = return_state.h
        # only first depth level returns new moves
        if current_state.g == 0:
            return return_state
        # other depths just pass up the heuristic value
        current_state.h = return_state.h
        return current_state


# State class
# holds state data
# id = stringified representation
# g = node depth
# h = heuristic value
# side = 'b' or 'w'
class State:
    __slots__ = ("id", "g", "h", "side")

    def __init__(self):
        self.id = ""
        self.g = self.h = 0

    # compare states by h = heuristic value
    def __lt__(self, other):
        return self.h < other.h


# Check if the start board is valid.
# @param start_state Array representing the state
# @return width (widest row size) on success
# @return None on validation failure
def validate_board(start_state):
    if type(start_state) is not list:
        print("Error: initial state is not a list.")
        return None
    n_row0 = len(start_state[0])
    if n_row0 < 4:
        print("Error: first row must be at least width 4.")
        return None
    # depth maximum
    row_depth = n_row0 - 2
    n_row_last = n_row0 + 1
    position = 0
    for i in range(row_depth, -1, -1):
        n_row_last = n_row_last - 1
        for j in range(0, n_row_last):
            position = position + 1
    n_row_last = 2
    n = -1 * row_depth - 1
    for i in range(-1, n, -1):
        n_row_last = n_row_last + 1
        for j in range(0, n_row_last):
            position = position + 1
    positions_max = n_row0 * n_row0 + n_row0 - 4
    if positions_max != position:
        print("Error: expected", positions_max, "positions, but got", position, ".")
        return None
    return n_row0


# Check win state
# @param state_id string representing the state
# @return false if no winner else returns 'w' or 'b' depending on who won
def check_win_board(state_id):
    pos_tot = len(state_id)
    width = pos_tot_to_width(pos_tot)
    state_id_beginning = state_id[0:pos_tot - width]
    state_id_end = state_id[pos_tot - width:pos_tot]
    # check all rows except last are 'w'
    if state_id_beginning.find('w') == -1:
        if state_id_end.find('w') == -1:
            return 'b'
        else:
            return 'w'
    # check all rows except last are 'b'
    if state_id_beginning.find('b') == -1:
        if state_id_end.find('b') == -1:
            return 'w'
        else:
            return 'b'
    return None


# heuristic or static board evaluator
# @param state_id string representing the state
# @param side character 'b' or 'w', which side to play
# @return Integer representing score of board
# score = your side pieces - opponent side pieces
# or if winning board then score = total positions on board
# else if opponent wins then score = negative total positions on board
def calculate_heuristic(state_id, side):
    pos_tot = len(state_id)
    if side == 'b':
        opponent = 'w'
    else:
        opponent = 'b'
    # winning board then score = total positions on board
    side_win = check_win_board(state_id)
    if side_win == side:
        return pos_tot
    elif side_win == opponent:
        return -1 * pos_tot
    num_b = state_id.count("b")
    num_w = state_id.count("w")
    score = 1
    if side == 'b':
        return num_b - num_w
    return num_w - num_b


# movegen function generates moves
# @param state_array Array representing the state
# @param side character 'b' or 'w', which side to play
# @return List of serialized states.
# it is up to the adversarial state search function in assignment 4
# to remove states that have already been visited
# Board position naming
# -------------------
# | 00 | 01 | 02 | 03 |
# -------------------
#   | 04 | 05 | 06 |
#    --------------
#      | 07 | 08 |
#    --------------
#   | 09 | 10 | 11 |
# -------------------
# | 12 | 13 | 14 | 15 |
# -------------------
def movegen(state_array, side):
    new_state_list = []
    # first the array is serialized
    state_id = serialize(state_array)
    width = len(state_array[0])
    pos_row_table = get_pos_row_table(width)
    pos_tot = width_to_pos_tot(width)
    rows_tot = width_to_rows_tot(width)
    if side == 'b':
        opponent = 'w'
    else:
        opponent = 'b'
    for pos in range(0, pos_tot):
        if state_id[pos] == side:
            row_info = pos_row_table[pos]
            # blue goes up
            if side == 'b':
                new_state_id = try_top_left(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
                new_state_id = try_top_right(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
            # white goes up
            if side == 'w':
                new_state_id = try_bottom_left(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
                new_state_id = try_bottom_right(state_id, side, opponent, rows_tot, pos, pos_row_table, -1)
                if new_state_id is not None:
                    new_state_list.append(new_state_id)
    # DEBUG - DELETE IN FINAL SUBMISSION
    # printPath(new_state_list)
    return new_state_list


# @param state_array Array representing the state
# @return string representing the state
# state[] example:
#  -------------------
# |  W |  W |  W |    |
#  -------------------
#   |    |    |  W |
#    --------------
#      |    |    |
#    --------------
#   |    |    |    |
#  -------------------
# |  B |  B |  B |  B |
#  -------------------
# becomes =>
# State.id: WWW---W-----BBBB
def serialize(state_array):
    return ''.join(state_array)


# unserialize() reverses as serialize()
# @param state_id string representing the state
# @return state_array Array representing the state
def unserialize(start_state_id):
    state_array = []
    pos_tot = len(start_state_id)
    width = pos_tot_to_width(pos_tot)
    row_depth = width - 2
    width_last = width
    position = 0
    # -row_depth to 0
    for i in range(-1 * row_depth, 1):
        str = ""
        for j in range(0, width_last):
            str += start_state_id[position]
            position = position + 1
        state_array.append(str)
        width_last = width_last - 1
    width_last = 3
    # 1 to row_depth
    for i in range(1, row_depth + 1):
        str = ""
        for j in range(0, width_last):
            str += start_state_id[position]
            position = position + 1
        state_array.append(str)
        width_last = width_last + 1
    return state_array


# @param width Max width of board.
# @return python dictionary
# that acts as table for position => row info
def get_pos_row_table(width):
    pos_row_table = {}
    pos_tot = width_to_pos_tot(width)
    for pos in range(0, pos_tot):
        row: int
        row, row_pos, row_width, row_depth = pos_to_row(pos, width)
        row_info = {}
        row_info["row"] = row
        row_info["row_pos"] = row_pos
        row_info["row_width"] = row_width
        row_info["row_depth"] = row_depth
        pos_row_table[pos] = row_info
    return pos_row_table


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_top_left(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == 0:
        return None
    if row_info["row_depth"] > 0 and row_info["row_pos"] == 0:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth <= 0:
        row_depth = abs(row_depth) + 1
    pos_try = pos - (row_depth + 2)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_top_left(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_top_right(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == 0:
        return None
    if row_info["row_depth"] > 0 and row_info["row_pos"] == row_info["row_width"] - 1:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth <= 0:
        row_depth = abs(row_depth) + 1
    pos_try = pos - (row_depth + 1)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_top_right(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_bottom_left(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == rows_tot - 1:
        return None
    if row_info["row_depth"] < 0 and row_info["row_pos"] == 0:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth >= 0:
        row_depth = abs(row_depth) + 1
    else:
        row_depth = abs(row_depth)
    pos_try = pos + (row_depth + 1)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_bottom_left(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# try to move the piece in direction
# pos_before is the original position when considering a jump
def try_bottom_right(state_id, side, opponent, rows_tot, pos, pos_row_table, pos_before):
    row_info = pos_row_table[pos]
    if row_info["row"] == rows_tot - 1:
        return None
    if row_info["row_depth"] < 0 and row_info["row_pos"] == row_info["row_width"] - 1:
        return None
    new_state_list = list(state_id)
    row_depth = row_info["row_depth"]
    if row_depth >= 0:
        row_depth = abs(row_depth) + 1
    else:
        row_depth = abs(row_depth)
    pos_try = pos + (row_depth + 2)
    if state_id[pos_try] == '-':
        new_state_list[pos_try] = side
        new_state_list[pos] = '-'
        if pos_before > -1:
            # resolve jump
            new_state_list[pos_before] = '-'
        return ''.join(new_state_list)
    elif pos_before == -1 and state_id[pos_try] == opponent:
        # try jump
        return try_bottom_right(state_id, side, opponent, rows_tot, pos_try, pos_row_table, pos)
    return None


# convert board total board positions to first row width
def pos_tot_to_width(pos_tot):
    return int((-1 + int(math.sqrt(17 + 4 * pos_tot))) / 2)


# convert first row width to board total board positions
def width_to_pos_tot(width):
    return int(width * width + width - 4)


# convert first row width to board total board positions
def width_to_rows_tot(width):
    return int(2 * width - 3)


# convert pos to row number and row position
# @param width Max width of board.
# @return row The row number starting from 0 and increasing downward.
# @return row_pos The position on the row starting from 0 and increasing right.
# @return row_width The width of the row
# @return row_depth The depth of the rwo from the shortest row
# negative goes upward and positive down, zero is center
def pos_to_row(pos, width):
    rows_tot = width_to_rows_tot(width)
    pos_tot = width_to_pos_tot(width)
    pos_mid = pos_tot / 2 - 1
    # this mathematical series calculation below has
    # has only been tested with width < 6
    if pos <= pos_mid + 1:
        row_depth_float = (((-1 + math.sqrt(8 * pos_mid - 8 * pos + 25)) / 2) - 2) * -1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        # but is sufficient for this assignment
        row_pos = math.ceil((row_depth_float - row_depth) * row_width)
    else:
        row_depth_float = ((-1 + math.sqrt(8 * pos - 8 * pos_mid + 9)) / 2) - 1
        row_depth = int(math.floor(row_depth_float))
        row_width = abs(row_depth) + 2
        # row position calculation may break on large widths
        row_pos = math.floor((row_depth_float - row_depth) * row_width)
    # width of the row
    row = int(row_depth + (rows_tot - 1) / 2)
    return row, row_pos, row_width, row_depth


# writes the stateId to a readable board on the console
# example:
#  -------------------
# |  W |  W |  W |    |
#  -------------------
#   |    |    |  W |
#    --------------
#      |    |    |
#    --------------
#   |    |    |    |
#  -------------------
# |  B |  B |  B |  B |
#  -------------------
def print_state(state_id):
    pos_tot = len(state_id)
    width = pos_tot_to_width(pos_tot)
    rows_tot = width_to_rows_tot(width)
    print(' ' * 2, end='')
    print('-' * 3 * width)
    for pos in range(0, pos_tot):
        row, row_pos, row_width, row_depth = pos_to_row(pos, width)
        indent = width - row_width
        if row_pos == 0:
            print(' ' * 2 * indent, end='')
            print("| ", end='')
        else:
            print(" | ", end='')
        if state_id[pos] != '-':
            print(state_id[pos], end='')
        else:
            print(' ', end='')
        if row_pos == row_width - 1:
            print(" |")
            print(' ' * 2 * (indent + 1), end='')
            print('-' * 3 * row_width)
