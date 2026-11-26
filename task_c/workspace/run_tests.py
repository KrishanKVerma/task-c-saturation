#!/usr/bin/env python3
"""The repository's own test runner. Standard library only.

    python3 run_tests.py

Exits non-zero if any test fails. One test is known to fail on a clean
checkout; see STATS-114 in the module docstring.
"""
import sys

import stats

tests = []


def test(name):
    def deco(fn):
        tests.append((name, fn))
        return fn
    return deco


@test("mean of a non-empty list")
def _():
    assert stats.mean([1, 2, 3]) == 2.0


@test("mean of an empty list is 0.0")
def _():
    assert stats.mean([]) == 0.0


@test("median of an odd-length list")
def _():
    assert stats.median([3, 1, 2]) == 2


@test("median of an even-length list averages the middle two")
def _():
    assert stats.median([1, 2, 3, 4]) == 2.5


@test("variance of a non-empty list")
def _():
    assert stats.variance([1, 2, 3]) == 2 / 3


def main():
    failed = 0
    for name, fn in tests:
        try:
            fn()
            print(f"PASS  {name}")
        except Exception as exc:
            failed += 1
            print(f"FAIL  {name}   <- {type(exc).__name__}: {exc}")
    print(f"\n{len(tests) - failed}/{len(tests)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
