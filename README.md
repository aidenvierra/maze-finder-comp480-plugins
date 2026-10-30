# Maze Path

A `nanoagent.plugin/v0001` plugin, created by `nanoagent plugin new` with the
structure of NanoAgent's reference plugin,
[arxiv-source](https://github.com/zeyuyang8/arxiv-source).

## Tools

Each maze is a fixed grid of text in `src/plugin/mazes.py` (# wall, . floor, S start,
G goal), from 7x7 to 29x17; most have several routes and one has no route at
all. The agent must find a shortest path, or show there is none, within 12
tool calls per maze. No network is used.

| Tool | Does | Code |
|---|---|---|
| `get_maze` | Returns a maze's rows, width and height | `src/plugin/mazes.py` |
| `walk` | Follows U/D/L/R moves from S and reports where they stop | `src/plugin/mazes.py` |
| `maze_record` | Returns the maze; only the verifier's reference | `src/plugin/mazes.py` |

`src/plugin/budget.py` caps the agent at 12 tool calls per maze; after that
every tool fails and asks it to submit.

### Tasks

| Task | Does | Runner |
|---|---|---|
| `get-maze` | Shows a maze | `tool`, with `get_maze` |
| `solve-maze` | Finds a shortest path from S to G, or reports there is none | `agent`, with `get_maze`, `walk`; reference `maze_record` |

The verifier computes the true shortest length by breadth-first search over the
pinned maze and replays the submitted moves. A path is valid only if it never
hits a wall, ends on G and is as short as the shortest; a longer path that
arrives scores shortest/length. For a maze with no route, only
`reachable: false` with no moves is valid.

A submission with `gave_up: true` always fails (invalid, score 0); its attempt's own score is kept
in the verdict details as `attempt_score`.

## Layout

```text
.
├── nanoagent.yaml   # manifest (a slimconfig ManifestConfig): id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env             # environment variable NAMEs this plugin needs, never values
├── src/plugin/      # the MCP server: __main__.py, its IMPLEMENTATIONS, and the plugin's own modules
├── tests/
├── ui/              # how the page draws the outputs: renderers.js and renderers.css
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier package
```

`contract.py` is the one place a value's shape is declared. Its `Output`
classes are the JSON Schemas the server offers and the agent sees, and every
input and output is built into its class on the way in and out: the server,
NanoAgent and the verifier all get typed values, never loose dicts. A tool
that fails raises; NanoAgent sees an MCP error.

To add a tool: add a `Tool` member, its input and output classes and its
`TOOLS` entry to `contract.py` (a snake_case name, classes named `...Input`
and `...Output`); write its implementation in `src/plugin/`, taking its input
and the workspace and returning its output; write its `verify_input` /
`verify_output` in `verifier/`, and tests for both. Then register it in
`src/plugin/__main__.py` (`IMPLEMENTATIONS`), `verifier/__init__.py` (`TOOLS`),
`nanoagent.yaml` (`tools`) and this README's Tools table; a task goes in its
Tasks table.

`LICENSE` stays the template's MIT license under your name, `.gitignore`
keeps its entries, and this README keeps its title and sections: NanoAgent refuses a plugin
that changes them (rule 10 of `nanoagent.plugin.manifest`). Renaming the
plugin means renaming it in `nanoagent.yaml` and this title together.

To add a task, add a `Task` member (a kebab-case id) and its `TASKS` input and
output classes to `contract.py`, and declare it in `nanoagent.yaml` with its `runner` (`tool`,
`agent` or `decide`) and a `reference` tool, or `null` if it has none. A `tool`
task's classes are its tool's; an `agent` task's agent ends by calling `submit`
with the task's output; a `decide` task's model only chooses, and every tool
argument and output field is an Enum or bool, or copied from a value of exactly
its type in the task's input or an earlier tool output. Then add the check of
its output, `verify_task(arguments, output, reference, workspace)`, to `TASKS`
in `verifier/__init__.py`. People use the plugin by chatting with its agent,
which runs its tasks and shows each output on the page (see `ui/`).

## Develop and run

```bash
uv sync --extra dev
uv run pytest
```

Publishing checks every plugin rule: push the plugin to a public GitHub
repository and run `rush publish <server> <github-url>`.
