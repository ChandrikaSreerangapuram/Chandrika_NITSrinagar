def inr_to_float(s: str) -> float:
    return float(s.replace("₹", "").replace(",", "").strip())
