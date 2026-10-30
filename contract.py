"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    GET_MAZE = "get_maze"
    WALK = "walk"
    MAZE_RECORD = "maze_record"


class Task(Enum):
    GET_MAZE = "get-maze"
    SOLVE_MAZE = "solve-maze"


MOVES = "Moves from S, one letter each: U up, D down, L left, R right, e.g. RRDDL"
PATH_MOVES = (
    "The moves of a shortest path from S to G, one letter each (U up, D down, L left, R right), e.g. RRDDL;"
    " empty when G cannot be reached"
)


GAVE_UP = (
    "True only if you could not solve it: then submit your best partial attempt, or empty values."
    " False when you believe your answer is right"
)


@dataclass
class PuzzleInput(Output):
    puzzle_id: Annotated[str, "The maze's id, e.g. maze-01"]


@dataclass
class MazeOutput(Output):
    puzzle_id: Annotated[str, "The maze's id, as given"]
    rows: Annotated[
        list[str], "The maze, top row first: # is a wall, . is open floor, S is the start and G is the goal"
    ]
    width: Annotated[int, "Characters per row"]
    height: Annotated[int, "Number of rows"]


@dataclass
class WalkInput(Output):
    puzzle_id: Annotated[str, "The maze's id"]
    moves: Annotated[str, MOVES]


@dataclass
class WalkOutput(Output):
    row: Annotated[int, "The row where the walk stopped, 0 for the top row"]
    col: Annotated[int, "The column where the walk stopped, 0 for the leftmost column"]
    moves_made: Annotated[int, "How many moves were made before the walk ended or hit a wall"]
    hit_wall: Annotated[bool, "Whether a move ran into a wall, which stops the walk there"]
    reached_goal: Annotated[bool, "Whether the walk stopped on G"]


@dataclass
class PathOutput(Output):
    reachable: Annotated[bool, "Whether G can be reached from S at all"]
    moves: Annotated[str, PATH_MOVES]
    gave_up: Annotated[bool, GAVE_UP]


TOOLS = {
    Tool.GET_MAZE: (PuzzleInput, MazeOutput),
    Tool.WALK: (WalkInput, WalkOutput),
    Tool.MAZE_RECORD: (PuzzleInput, MazeOutput),
}
TASKS = {
    Task.GET_MAZE: (PuzzleInput, MazeOutput),
    Task.SOLVE_MAZE: (PuzzleInput, PathOutput),
}
