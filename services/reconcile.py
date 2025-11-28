from typing import List, Dict
from models.schema import LineItem, Taxes

def deduplicate_items(items: List[LineItem]):
    seen = set()
    out = []
    for it in items:
        key = (it.description.lower().strip(), round(it.amount, 2))
        if key not in seen:
            seen.add(key)
            out.append(it)
    return out

def compute_subtotals(text: str, items):
    import re
    subs = []
    m = re.search(r"(Subtotal|Total Amount).*?(₹[\d,]+)", text, re.I | re.DOTALL)
    if m:
        subs.append({"label": m.group(1), "amount": float(m.group(2).replace("₹", "").replace(",", ""))})
    return subs

def sum_items(items):
    return round(sum(i.amount for i in items), 2)

def compute_final_total(items_sum, discount, taxes_total, round_off, printed_final=None):
    calc = round(items_sum - (discount or 0) + (taxes_total or 0) + (round_off or 0), 2)
    if printed_final is not None:
        return printed_final
    return calc

def build_taxes_dict(totals):
    details = {}
    for k in ["CGST", "SGST", "IGST"]:
        if k in totals:
            details[k] = totals[k]

    total_tax = totals.get("total_tax", sum(details.values()) if details else None)
    return Taxes(details=details, total_tax=total_tax)
