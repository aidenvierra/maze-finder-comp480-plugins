from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, PuzzleInput, Task, Tool
from plugin import get_maze, maze_record

SOLUTIONS = {"maze-01": "RRRRDDLLDDRR"}


# The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
def verify_input(tool: str, value: dict) -> dict:
    return verifier.verify_input(tool, build_output(value, TOOLS[Tool(tool)][0]))


def verify_output(tool: str, given: dict, made: dict, workspace: Path) -> dict:
    classes = TOOLS[Tool(tool)]
    return verifier.verify_output(tool, build_output(given, classes[0]), build_output(made, classes[1]), str(workspace))


def solve(workspace: Path, puzzle_id: str, output: dict, reference: dict | None = None) -> dict:
    given, made = TASKS[Task.SOLVE_MAZE]
    if reference is None:
        reference = plain_output(maze_record(PuzzleInput(puzzle_id=puzzle_id), workspace))
    pinned = build_output(reference, TOOLS[Tool.MAZE_RECORD][1]) if reference else None
    return verifier.verify_task(
        "solve-maze",
        build_output({"puzzle_id": puzzle_id}, given),
        build_output({"gave_up": False} | output, made),
        pinned,
        str(workspace),
    )


def test_approves_a_shortest_path(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": "RRRRDDLLDDRR"})
    assert verdict["valid"] is True and verdict["score"] == 1.0 and verdict["details"]["shortest"] == 12


def test_a_longer_path_that_arrives_gets_partial_credit(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": "RLRRRRDDLLDDRR"})
    assert verdict["valid"] is False and verdict["score"] == round(12 / 14, 4) and "longer" in verdict["message"]


@pytest.mark.parametrize(
    ("moves", "message"),
    [
        ("RRRRRDDLLDDRR", "wall"),  # walks into the wall at the corridor's end
        ("UUU", "wall"),  # leaves through the top
        ("RRRRDD", "does not end on G"),
        ("", "does not end on G"),
        ("RRRRDDLLDDRRX", "U, D, L and R"),
        ("rrrrddllddrr", "U, D, L and R"),
    ],
)
def test_refuses_wrong_or_malformed_paths(tmp_path: Path, moves: str, message: str) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": moves})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and message in verdict["message"]


def test_refuses_unreachable_when_a_path_exists(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": False, "moves": ""})
    assert verdict["valid"] is False and "a path exists" in verdict["message"]


def test_sealed_maze_needs_unreachable_and_no_moves(tmp_path: Path) -> None:
    assert solve(tmp_path, "maze-05", {"reachable": False, "moves": ""})["valid"] is True
    assert solve(tmp_path, "maze-05", {"reachable": False, "moves": "D"})["valid"] is False
    verdict = solve(tmp_path, "maze-05", {"reachable": True, "moves": "DDDD"})
    assert verdict["valid"] is False and "no path" in verdict["message"]


@pytest.mark.parametrize(
    ("puzzle_id", "shortest"), [("maze-02", 16), ("maze-03", 40), ("maze-04", 48), ("maze-06", 104)]
)
def test_knows_each_mazes_shortest_length(tmp_path: Path, puzzle_id: str, shortest: int) -> None:
    verdict = solve(tmp_path, puzzle_id, {"reachable": False, "moves": ""})
    assert verdict["details"]["shortest"] == shortest


def test_refuses_to_judge_without_the_maze(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": "R"}, reference={})
    assert verdict["valid"] is False and "maze" in verdict["message"]


def test_get_maze_tool_task_and_tool_checks(tmp_path: Path) -> None:
    given = {"puzzle_id": "maze-01"}
    made = plain_output(get_maze(PuzzleInput(**given), tmp_path))
    task_given, task_made = TASKS[Task.GET_MAZE]
    check = verifier.verify_task("get-maze", build_output(given, task_given), build_output(made, task_made), None, "")
    assert check["valid"] is True
    assert verify_output("get_maze", given, made | {"width": 8}, tmp_path)["valid"] is False
    assert verify_output("get_maze", given, made | {"rows": ["#S#", "#.#"]}, tmp_path)["valid"] is False
    assert verify_input("get_maze", {"puzzle_id": "maze-01"})["valid"] is True
    assert verify_input("walk", {"puzzle_id": "maze-01", "moves": "UDLR"})["valid"] is True
    assert verify_input("walk", {"puzzle_id": "maze-01", "moves": "UP"})["valid"] is False
    walked = {"row": 1, "col": 5, "moves_made": 4, "hit_wall": False, "reached_goal": False}
    assert verify_output("walk", {"puzzle_id": "maze-01", "moves": "RRRR"}, walked, tmp_path)["valid"] is True
    assert verify_output("walk", {"puzzle_id": "maze-01", "moves": "RR"}, walked, tmp_path)["valid"] is False


def test_giving_up_is_a_failure_with_the_attempt_kept_in_details(tmp_path: Path) -> None:
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": "RRRRDDLLDDRR", "gave_up": True})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and "gave up" in verdict["message"]
    assert verdict["details"]["attempt_score"] == 1.0
    verdict = solve(tmp_path, "maze-01", {"reachable": True, "moves": "", "gave_up": True})
    assert verdict["valid"] is False and verdict["score"] == 0.0 and verdict["details"]["gave_up"] is True
