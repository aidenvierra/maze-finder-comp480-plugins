"""The deterministic verifier: each tool's checks live in its own class, on contract instances."""

from contract import Task, Tool

from .maze import GetMaze, Walk, verify_get_maze, verify_solve

TOOLS = {
    Tool.GET_MAZE: GetMaze,
    Tool.WALK: Walk,
    Tool.MAZE_RECORD: GetMaze,
}
# task -> its output's check, verify_task(arguments, output, reference, workspace)
TASKS = {
    Task.GET_MAZE: verify_get_maze,
    Task.SOLVE_MAZE: verify_solve,
}


def verify_input(tool, value):
    return TOOLS[Tool(tool)].verify_input(value)


def verify_output(tool, input_value, output_value, workspace):
    return TOOLS[Tool(tool)].verify_output(input_value, output_value, workspace)


def verify_task(task, arguments, output, reference, workspace):
    return TASKS[Task(task)](arguments, output, reference, workspace)
