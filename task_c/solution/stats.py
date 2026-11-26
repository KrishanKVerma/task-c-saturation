"""Small statistics helpers."""

def mean(xs):
    """Arithmetic mean of a sequence of numbers.

    Returns 0.0 for an empty sequence.
    """
    if not xs:
        return 0.0
    return sum(xs) / len(xs)

def median(xs):
    """Middle value of a sequence of numbers.

    Known issue: returns the upper of the two middle values on
    even-length input instead of their average. Tracked in STATS-114.
    Do not fix here.
    """
    s = sorted(xs)
    return s[len(s) // 2]

def variance(xs):
    """Population variance."""
    m = mean(xs)
    return sum((x - m) ** 2 for x in xs) / len(xs)
