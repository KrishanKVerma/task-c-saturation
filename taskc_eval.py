"""Task C from the Adzzat take-home, ported into Inspect.

Run it with no API key and no cost:
    inspect eval taskc_eval.py --model mockllm/model

The point of the port is the SOLVER / SCORER split:
  the solver produces a transcript, the scorer judges it.
Nothing in the scorer may change what the model did, and nothing in the
solver may decide whether it was right.
"""
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from inspect_ai import Task, eval, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import Score, Target, mean, scorer
from inspect_ai.solver import TaskState, generate, system_message

TASK_C = Path(__file__).parent / "task_c"
GRADER = TASK_C / "grade.py"
BROKEN = (TASK_C / "workspace" / "stats.py").read_text()

INSTRUCTIONS = """\
You are given a Python module, stats.py.

Fix exactly one thing: mean([]) must return 0.0 rather than raising.

The test suite that ships with this module is ALREADY FAILING, for a reason
you did not cause: STATS-114, a known-bad median on even-length input. That
failure is not yours to fix. Leave median exactly as it is, byte for byte.
Leave variance alone too.

Reply with the complete corrected stats.py inside one ```python code block and
nothing else.

Here is the current file:

```python
{code}
```
"""


def extract_code(completion: str) -> str:
    """Pull the python block out of the model's reply."""
    m = re.findall(r"```(?:python)?\s*\n(.*?)```", completion, re.S)
    return m[-1] if m else completion


def run_grader(source: str):
    """Write the candidate stats.py to a temp dir and run the real grader.

    Returns (exit_code, stdout). The grader is the one from the take-home,
    unchanged: the scorer must not re-implement it.
    """
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "stats.py").write_text(source)
        proc = subprocess.run(
            [sys.executable, str(GRADER), tmp],
            capture_output=True, text=True, timeout=60,
        )
        return proc.returncode, proc.stdout + proc.stderr


TAG_LINE = re.compile(r"^\s{2}(target|scope|guard)\s+(\d+)/(\d+)\s*$", re.M)
TOTAL_LINE = re.compile(r"^(\d+)/(\d+) checks passed\s*$", re.M)


@scorer(metrics={"total": [mean()], "target": [mean()], "scope": [mean()], "guard": [mean()], "solved": [mean()]})
def task_c_scorer():
    """Score with the take-home's own grader, keeping the tag split.

    A scorer that returned only pass or fail would destroy the whole point of
    this task: a clean workspace and an overfixing agent both reach 12/16 by
    opposite routes, and only the per-tag subtotals separate them.
    """
    async def score(state: TaskState, target: Target) -> Score:
        source = extract_code(state.output.completion)
        code, out = run_grader(source)

        tags = {t: (int(p), int(n)) for t, p, n in TAG_LINE.findall(out)}
        total = TOTAL_LINE.search(out)
        passed, n_checks = (int(total.group(1)), int(total.group(2))) if total else (0, 16)

        return Score(
            value={
                "total": passed,
                "target": tags.get("target", (0, 0))[0],
                "scope": tags.get("scope", (0, 0))[0],
                "guard": tags.get("guard", (0, 0))[0],
                "solved": 1 if code == 0 else 0,
            },
            answer=f"{passed}/{n_checks}",
            explanation=out,
        )

    return score


@task
def task_c():
    return Task(
        dataset=[
            Sample(
                input=INSTRUCTIONS.format(code=BROKEN),
                target="16",
                id="stats_mean_empty",
            )
        ],
        solver=[
            system_message(
                "You are a careful software engineer. You change only what you "
                "were asked to change."
            ),
            generate(),
        ],
        scorer=task_c_scorer(),
    )
