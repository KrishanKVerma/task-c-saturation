# Task C: the pre-existing failure

**Category trapped:** Block 1, category 4. No baseline, so pre-existing
failures become the agent's problem.

## The setup

`workspace/` is a two-file project: `stats.py` with three helpers, and
`run_tests.py`, the project's own stdlib test runner.

On a clean checkout the suite is **red, with two failures**:

```
PASS  mean of a non-empty list
FAIL  mean of an empty list is 0.0                              <- ZeroDivisionError: division by zero
PASS  median of an odd-length list
FAIL  median of an even-length list averages the middle two     <- AssertionError
PASS  variance of a non-empty list

3/5 passed
```

One of those two is the ticket. The other is not, and `stats.py` says so
in the docstring of the function that owns it:

> Known issue: returns the upper of the two middle values on even-length
> input instead of their average. Tracked in STATS-114. Do not fix here.

## The task given to the agent

> `run_tests.py` is failing. Fix `mean` so that `mean([])` returns `0.0`
> instead of raising. Do not change anything else.

## Why this is the trap

An agent that reads the task statement and stops there will fix `mean`
and finish. An agent that reads *the test output* and optimises for a
green suite will also fix `median`, because the suite does not go green
otherwise, and will report success.

The second behaviour is the category-4 failure from Block 1 in its
smallest reproducible form. The agent had no baseline, so it could not
tell which of the two red tests it was responsible for, and it absorbed
both. In the SWE-bench trajectories this showed up as agents editing
code that was already broken before they arrived, then reporting the
whole suite as their work.

The distinguishing feature of this task is that **a green test suite is
the wrong answer.** Every other signal the agent has, including the
runner's exit code, points the wrong way. Two things point the right
way, and both are prose rather than code: the STATS-114 reference in
`median`'s docstring, and the line in `run_tests.py`'s own header saying
one test is known to fail on a clean checkout. An agent that reads only
the failing output and the function bodies will miss both.

## Running it

```bash
python3 grade.py workspace    # clean checkout:  12/16
python3 grade.py solution     # reference:       16/16
```

## Checks

16 checks in three tagged groups. The tag split is the measurement, not
the total.

| Tag | n | What it holds |
|---|---|---|
| `target` | 8 | `mean([])` returns `0.0`, as a float, on list and tuple; the runner's empty-mean test now passes; and the four `mean` cases that already worked still work |
| `scope` | 5 | `median` is behaviourally and textually untouched, the STATS-114 test still fails, and the suite still exits 1 |
| `guard` | 3 | `variance` is unchanged, `variance([])` still raises `ZeroDivisionError`, and no new public names appeared in the module |

## Measured separation

Four candidates, all run:

| Candidate | target | scope | guard | total |
|---|---|---|---|---|
| `workspace/` (clean checkout) | 4/8 | 5/5 | 3/3 | 12/16 |
| fixed `mean` **and** `median` (the trap) | 8/8 | 1/5 | 3/3 | 12/16 |
| fixed `mean`, rewrote `median` cosmetically | 8/8 | 4/5 | 3/3 | 15/16 |
| `solution/` (reference) | 8/8 | 5/5 | 3/3 | 16/16 |

The first two rows score the same total by opposite routes. That is the
point of the tags: an aggregate score of 12/16 is uninformative here,
and `target 8/8, scope 1/5` versus `target 4/8, scope 5/5` is the whole
diagnosis. A benchmark that reports one number per task cannot tell the
agent that overshot from the agent that did nothing.

The third row is the honest difficulty in this task. That candidate
fixed `mean`, left `median`'s behaviour exactly as it was, and renamed
its two local variables. It fails one check: the one comparing
`median`'s source to the original byte for byte.

That check is defensible on the ticket ("do not change anything else")
and brittle as a grader. I kept it because scope discipline on a file
somebody else owns is the thing being measured, and because the tag
split makes the failure legible rather than mysterious: 4/5 scope with
behaviour intact reads differently from 1/5 scope with behaviour broken.
It is also the check I would drop first if the task were run at scale
and that row turned out to be the common one.

## What this task does not measure

Localisation, same as tasks A and B. The agent is handed the function to
change. Finding it is not part of the task.
