# task-c-saturation

An Inspect eval for a tagged code-repair task, plus 46 runs showing that the
task cannot tell apart models differing 300-fold in size.

The task gives a model a small statistics module with one deliberate defect, a
stated scope it must not exceed, and constraints it must respect. A grader
scores those three things separately.

## The result

| Model | n | Solved | Mean total |
|---|---|---|---|
| nemotron-3-ultra-550b-a55b | 20 | 20/20 | 16.00 |
| nemotron-3.5-lightning | 20 | 20/20 | 16.00 |
| liquid/lfm-3-1.7b | 6 | 6/6 | 16.00 |

All 46 samples scored 16 of 16. The Wilson 95% interval on each 20-run arm is
[83.9%, 100%].

A 1.7B model and a 550B model are indistinguishable here. The task is
saturated: there is no band in which it discriminates at all. That is a fact
about the task, not a finding about the models.

I wrote this task myself, one of three for a benchmark-design exercise, and the
notes I submitted with it said none of the three tested localisation. That was
a guess. This repository is the measurement.

## What the harness does

`taskc_eval.py` defines a single-sample Inspect task carrying a broken
`stats.py`. The solver is `[system_message(...), generate()]`.

The scorer never reads the model's account of what it did. It takes the last
fenced Python block from the output, writes it to a temporary directory, and
runs the task's original `grade.py` unchanged as a subprocess. It parses the
grader's own output and returns five fields: `total`, `target`, `scope`,
`guard`, `solved`.

That separation is the point. An agent reporting success is not evidence of
success; the grader running against files on disk is.

## Per-tag scoring

The grader scores three things separately instead of collapsing them into pass
or fail:

- `target` — was the intended defect fixed
- `scope` — did anything outside the intended scope change
- `guard` — were the stated constraints respected

`probe.py` pushes four synthetic candidates through the scorer with no model
call: did-nothing, reference solution, overfix, and prose containing no code.
The tags separate those four as designed.

No real model has ever triggered that separation. All 46 live runs took full
marks on every tag. The discrimination is demonstrated against synthetic
candidates only.

## Under tool use

The single-shot eval above hands the model the file and asks for a fix. To rule
out that the format itself was hiding a difference, `taskc_agent.py` re-runs the
same task as an agentic eval: each model gets a bash shell, a Python tool, a
Docker sandbox, and a 30-message budget. The scorer is unchanged — it still
pulls `stats.py` out of the container and runs the original grader out of
process, where the agent cannot reach it.

| Model | n | Solved | Mean total |
|---|---|---|---|
| nemotron-3-ultra-550b-a55b | 5 | 5/5 | 16.00 |
| liquid/lfm-3-1.7b | 3 | 3/3 | 16.00 |

Both ends of the size range score 16 of 16, identical to single-shot. A
`mockllm` agent that touches nothing scores 12/16, which fixes the do-nothing
floor. Tool access does not separate the models: the task is saturated in both
formats.

## Running it

```
pip install inspect-ai
inspect eval taskc_eval.py --model <provider>/<model>
python probe.py            # no model call, no API key
```

`logs/` holds the `.eval` files behind both tables above.

## Known limitations

- One sample, run repeatedly. This measures the task, not any model's general
  ability.
- Three models from two families. A wider sweep could still turn up a band.
- The scorer takes the last fenced Python block, so a model emitting several
  blocks, or none, is scored on that convention rather than on what it meant.

## What this is for

A benchmark that cannot separate a 1.7B model from a 550B one still reports a
number, and that number still gets read as a capability measurement. The cheap
check is to run a task across a wide range of model sizes before trusting it.
This is that check, run on one of my own tasks, with the result going against
me.
