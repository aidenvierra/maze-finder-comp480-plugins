"""Checks for each tool's calls and for the solve-maze submission, against the pinned maze."""

import re
from collections import deque

from .checks import gave_up_verdict, result

PUZZLE_ID = re.compile(r"^maze-\d{2}$")
MOVES = re.compile(r"^[UDLR]*$")
STEPS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def find(rows, mark):
    return [(r, c) for r, line in enumerate(rows) for c, char in enumerate(line) if char == mark]


def maze_problem(rows):
    if not rows or len({len(row) for row in rows}) != 1:
        return "the maze is not a rectangle"
    if any(char not in "#.SG" for row in rows for char in row):
        return "the maze holds characters other than # . S G"
    if len(find(rows, "S")) != 1 or len(find(rows, "G")) != 1:
        return "the maze needs exactly one S and one G"
    return None


def open_cell(rows, r, c):
    return 0 <= r < len(rows) and 0 <= c < len(rows[0]) and rows[r][c] != "#"


def shortest(rows):
    """The fewest moves from S to G, by breadth-first search; None when G cannot be reached."""
    start = find(rows, "S")[0]
    seen = {start: 0}
    queue = deque([start])
    while queue:
        r, c = queue.popleft()
        if rows[r][c] == "G":
            return seen[(r, c)]
        for dr, dc in STEPS.values():
            step = (r + dr, c + dc)
            if open_cell(rows, *step) and step not in seen:
                seen[step] = seen[(r, c)] + 1
                queue.append(step)
    return None


def replay(rows, moves):
    """(row, col) after the moves, and the index of the first move into a wall (-1 if none)."""
    r, c = find(rows, "S")[0]
    for index, move in enumerate(moves):
        dr, dc = STEPS[move]
        if not open_cell(rows, r + dr, c + dc):
            return (r, c), index
        r, c = r + dr, c + dc
    return (r, c), -1


def _puzzle_input(value):
    if not PUZZLE_ID.fullmatch(value.puzzle_id):
        return result(False, f"puzzle_id {value.puzzle_id!r} is not of the form maze-NN")
    return result(True, "input is valid")


class GetMaze:
    verify_input = staticmethod(_puzzle_input)

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        if output_value.puzzle_id != input_value.puzzle_id:
            return result(False, "the maze is for a different puzzle")
        problem = maze_problem(output_value.rows)
        if problem:
            return result(False, problem)
        if (output_value.width, output_value.height) != (len(output_value.rows[0]), len(output_value.rows)):
            return result(False, "width and height do not match the rows")
        return result(True, "maze returned")


class Walk:
    @staticmethod
    def verify_input(value):
        if not PUZZLE_ID.fullmatch(value.puzzle_id):
            return result(False, f"puzzle_id {value.puzzle_id!r} is not of the form maze-NN")
        if not MOVES.fullmatch(value.moves):
            return result(False, "moves may hold only U, D, L and R")
        return result(True, "input is valid")

    @staticmethod
    def verify_output(input_value, output_value, workspace):
        made = output_value.moves_made
        if not 0 <= made <= len(input_value.moves):
            return result(False, "moves_made is more than the moves given")
        if output_value.hit_wall == (made == len(input_value.moves)):
            return result(False, "a walk hits a wall exactly when it stops before its last move")
        return result(True, "walk is consistent")


def verify_get_maze(arguments, output, reference, workspace):
    return GetMaze.verify_output(arguments, output, workspace)


def _judge(arguments, output, reference, workspace):
    """Valid for the reachable flag and a path of the shortest length; a longer path scores shortest/length."""
    if reference is None or maze_problem(reference.rows):
        return result(False, "no usable maze was pinned, so the submission cannot be judged")
    rows = reference.rows
    best = shortest(rows)
    details = {"shortest": best, "submitted_length": len(output.moves)}
    if not MOVES.fullmatch(output.moves):
        return result(False, "malformed moves: only U, D, L and R are allowed", score=0.0, **details)
    if best is None:
        if output.reachable:
            return result(False, "there is no path from S to G, but reachable is true", score=0.0, **details)
        if output.moves:
            return result(False, "G cannot be reached, so moves must be empty", score=0.0, **details)
        return result(True, "correct: G cannot be reached from S", **details)
    if not output.reachable:
        return result(False, f"a path exists ({best} moves), but reachable is false", score=0.0, **details)
    (r, c), wall = replay(rows, output.moves)
    if wall != -1:
        return result(False, f"move {wall} ({output.moves[wall]}) runs into a wall", score=0.0, **details)
    if rows[r][c] != "G":
        return result(False, f"the path does not end on G; it stops at row {r}, column {c}", score=0.0, **details)
    if len(output.moves) > best:
        score = round(best / len(output.moves), 4)
        return result(False, f"the path reaches G but is longer than the shortest ({best})", score=score, **details)
    return result(True, f"a shortest path: {best} moves from S to G", **details)


def verify_solve(arguments, output, reference, workspace):
    return gave_up_verdict(_judge(arguments, output, reference, workspace), output)
