from __future__ import annotations

from pathlib import Path

import pytest

from contract import PuzzleInput, Tool, WalkInput
from plugin import get_maze, maze_record, walk
from plugin.budget import Budget, BudgetSpent
from plugin.mazes import MAZES


def test_get_maze_returns_the_grid(tmp_path: Path) -> None:
    maze = get_maze(PuzzleInput(puzzle_id="maze-01"), tmp_path)
    assert maze.rows == MAZES["maze-01"] and (maze.width, maze.height) == (7, 7)
    assert maze_record(PuzzleInput(puzzle_id="maze-01"), tmp_path) == maze
    with pytest.raises(ValueError, match="unknown puzzle"):
        get_maze(PuzzleInput(puzzle_id="maze-99"), tmp_path)


def test_every_maze_has_one_start_and_one_goal() -> None:
    for rows in MAZES.values():
        text = "".join(rows)
        assert text.count("S") == 1 and text.count("G") == 1 and len({len(row) for row in rows}) == 1


def test_walk_follows_moves_and_stops_at_a_wall(tmp_path: Path) -> None:
    # maze-01: S at (1, 1); the corridor runs right to (1, 5).
    moved = walk(WalkInput(puzzle_id="maze-01", moves="RRRR"), tmp_path)
    assert (moved.row, moved.col, moved.moves_made, moved.hit_wall, moved.reached_goal) == (1, 5, 4, False, False)
    blocked = walk(WalkInput(puzzle_id="maze-01", moves="RRRRRD"), tmp_path)
    assert (blocked.row, blocked.col, blocked.moves_made, blocked.hit_wall) == (1, 5, 4, True)
    solved = walk(WalkInput(puzzle_id="maze-01", moves="RRRRDDLLDDRR"), tmp_path)
    assert solved.reached_goal is True and solved.hit_wall is False
    assert walk(WalkInput(puzzle_id="maze-01", moves=""), tmp_path).moves_made == 0
    with pytest.raises(ValueError, match="U, D, L and R"):
        walk(WalkInput(puzzle_id="maze-01", moves="RX"), tmp_path)


def test_budget_allows_twelve_calls_per_maze() -> None:
    budget = Budget(limit=12)
    budget.charge(Tool.GET_MAZE, {"puzzle_id": "maze-01"})
    for _ in range(11):
        budget.charge(Tool.WALK, {})
    with pytest.raises(BudgetSpent, match="submit your best answer now, or set gave_up"):
        budget.charge(Tool.WALK, {})
    budget.charge(Tool.MAZE_RECORD, {})
    budget.charge(Tool.GET_MAZE, {"puzzle_id": "maze-02"})
    assert budget.used == 1
