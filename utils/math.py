def approx_equal(a: float, b: float, eps: float = 0.5) -> bool:
    return abs(a - b) <= eps
