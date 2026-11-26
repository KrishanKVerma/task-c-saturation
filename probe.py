"""Feed three candidates through the scorer without calling any model.

    python3 probe.py

This is how you check a scorer: give it known-good, known-bad and known-wrong
answers and see whether it separates them. A scorer you have never fed a wrong
answer to is a scorer you have not tested.
"""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location("te", "taskc_eval.py")
te = importlib.util.module_from_spec(spec)
spec.loader.exec_module(te)

TASK_C = Path("task_c")
reference = (TASK_C / "solution" / "stats.py").read_text()

candidates = {
    "did nothing": (TASK_C / "workspace" / "stats.py").read_text(),
    "reference solution": reference,
    "overfixed the pre-existing bug": reference.replace(
        "    s = sorted(xs)\n    return s[len(s) // 2]",
        "    s = sorted(xs)\n    n = len(s)\n"
        "    if n % 2 == 0:\n        return (s[n // 2 - 1] + s[n // 2]) / 2\n"
        "    return s[n // 2]",
    ),
    "prose, not code": "Sure! Here is the fixed file.",
}

print(f"{'candidate':34s} {'exit':>4}  {'total':>6}  {'target':>6}  {'scope':>5}  {'guard':>5}")
print("-" * 70)
for name, src in candidates.items():
    body = te.extract_code("```python\n" + src + "```")
    code, out = te.run_grader(body)
    tags = {t: (int(p), int(n)) for t, p, n in te.TAG_LINE.findall(out)}
    tot = te.TOTAL_LINE.search(out)
    total = f"{tot.group(1)}/{tot.group(2)}" if tot else "crash"
    cell = lambda k: f"{tags[k][0]}/{tags[k][1]}" if k in tags else "-"
    print(f"{name:34s} {code:>4}  {total:>6}  {cell('target'):>6}  "
          f"{cell('scope'):>5}  {cell('guard'):>5}")
