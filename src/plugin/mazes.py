from __future__ import annotations

from pathlib import Path

from contract import MazeOutput, PuzzleInput, WalkInput, WalkOutput

# Fixed mazes (# wall, . floor, S start, G goal), generated once with a seeded depth-first search and
# extra openings so most have several routes. maze-05's goal is walled in, so it cannot be reached.
MAZES = {
    "maze-01": ["#######", "#S....#", "#####.#", "#.#...#", "#.#.###", "#....G#", "#######"],
    "maze-02": [
        "###########",
        "#S......#.#",
        "#.#####.#.#",
        "#.#...#...#",
        "#.#.#.###.#",
        "#.#.#.....#",
        "#.#.#######",
        "#.#.#...#.#",
        "#.#.#.#.#.#",
        "#........G#",
        "###########",
    ],
    "maze-03": [
        "###############",
        "#S....#...#...#",
        "#####.#.#.#.#.#",
        "#...#.#.#...#.#",
        "#.#.#.#.###.###",
        "#.#...#.......#",
        "#.#######.#.#.#",
        "#.#.....#.#...#",
        "#.###.#.###.#.#",
        "#.....#.....#.#",
        "###########.#.#",
        "#.#...#.......#",
        "#.#.#.#.###.###",
        "#...#........G#",
        "###############",
    ],
    "maze-04": [
        "#####################",
        "#S..#...#...........#",
        "###.#.#.###.#######.#",
        "#.#...#.........#...#",
        "#.#############.#.###",
        "#.....#.......#.#...#",
        "#.#####.#.#.###.#.#.#",
        "#.#...............#.#",
        "#.#.#############.#.#",
        "#.#.....#.......#.#.#",
        "#.###.#.#.#######.#.#",
        "#.......#...#.....#.#",
        "#.#########.#.#####.#",
        "#.....#...#.....#...#",
        "#####.#.#.#######.#.#",
        "#.................#.#",
        "#.#####.#####.#.###.#",
        "#...#...#.....#.#...#",
        "###.#.###.#####.#.###",
        "#.....#.........#..G#",
        "#####################",
    ],
    "maze-05": [
        "#############",
        "#S#.....#...#",
        "#.#.#####.#.#",
        "#.#.......#.#",
        "#.#.###.#.#.#",
        "#...#.......#",
        "###.#.#####.#",
        "#.#...#...#.#",
        "#.#####.###.#",
        "#...#.......#",
        "#.###.#######",
        "#.........#G#",
        "#############",
    ],
    "maze-06": [
        "#############################",
        "#S..#...#.........#...#.....#",
        "###.#.#.###.#.###.#.#.#.#.#.#",
        "#...#.#...#.#...#.....#...#.#",
        "#.###.###.#.###.#####.#.#.#.#",
        "#.....#...#.#...#.....#.#.#.#",
        "#####.#.#####.###.#.#.###.#.#",
        "#.....#.#.....#...#.#.......#",
        "#.#.#.#.#.#####.#.#.###.#.#.#",
        "#...#...#.#.....#.#.......#.#",
        "#.#.#####.#.#.###.#######.#.#",
        "#.........#.#.....#...#...#.#",
        "#.#.#.#####.#######.#.#.###.#",
        "#.#...#.#...#.......#.#.....#",
        "#.#.###.#.#######.###.#######",
        "#...#.............#........G#",
        "#############################",
    ],
}
STEPS = {"U": (-1, 0), "D": (1, 0), "L": (0, -1), "R": (0, 1)}


def _maze(puzzle_id: str) -> list[str]:
    if puzzle_id not in MAZES:
        raise ValueError(f"unknown puzzle {puzzle_id!r}: the mazes are {', '.join(MAZES)}")
    return MAZES[puzzle_id]


def get_maze(given: PuzzleInput, workspace: Path) -> MazeOutput:
    rows = _maze(given.puzzle_id)
    return MazeOutput(puzzle_id=given.puzzle_id, rows=list(rows), width=len(rows[0]), height=len(rows))


def maze_record(given: PuzzleInput, workspace: Path) -> MazeOutput:
    return get_maze(given, workspace)


def walk(given: WalkInput, workspace: Path) -> WalkOutput:
    rows = _maze(given.puzzle_id)
    if any(move not in STEPS for move in given.moves):
        raise ValueError("moves may hold only U, D, L and R")
    row, col = next((r, c) for r, line in enumerate(rows) for c, char in enumerate(line) if char == "S")
    made = 0
    for move in given.moves:
        dr, dc = STEPS[move]
        nr, nc = row + dr, col + dc
        if not (0 <= nr < len(rows) and 0 <= nc < len(rows[0])) or rows[nr][nc] == "#":
            return WalkOutput(row=row, col=col, moves_made=made, hit_wall=True, reached_goal=rows[row][col] == "G")
        row, col, made = nr, nc, made + 1
    return WalkOutput(row=row, col=col, moves_made=made, hit_wall=False, reached_goal=rows[row][col] == "G")
