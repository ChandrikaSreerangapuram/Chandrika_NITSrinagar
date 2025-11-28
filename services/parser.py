import re
from typing import List, Dict
from models.schema import LineItem

AMOUNT_RE = r"(₹|INR|\bRs\.?)\s*([\d,]+(?:\.\d{1,2})?)"

def norm_money(s: str) -> float:
    return float(s.replace(",", "").strip())

def extract_header_fields(text: str) -> Dict[str, str]:
    fields = {}
    pairs = {
        "bill_no": r"Bill\s*No\.?\s*[:\-]\s*([A-Za-z0-9/\\\-]+)",
        "bill_date": r"Bill\s*Date\s*[:\-]\s*([0-9]{1,2}[-/][A-Za-z]{3}[-/][0-9]{2,4}|[0-9]{2}[-/][0-9]{2}[-/][0-9]{4})",
        "patient_name": r"Name\s*of\s*Patient\s*[:\-]\s*(.+)"
    }
    for k, pat in pairs.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            fields[k] = m.group(1).strip()
    return fields

def parse_line_items(text: str) -> List[LineItem]:
    items = []
    lines = [l.strip() for l in text.splitlines() if l.strip()]

    for line in lines:
        if re.search(r"(Total|Subtotal|Grand Total|Discount|CGST|SGST|Round Off)", line, re.I):
            continue

        m_qty = re.search(
            r"^(.*?)(₹[\d,]+)\s*/\w+\s*[x×]\s*([\d.]+)\s*=\s*(₹[\d,]+)",
            line, re.I
        )
        if m_qty:
            desc = m_qty.group(1).strip(":- ")
            unit = norm_money(m_qty.group(2)[1:])
            qty = float(m_qty.group(3))
            amt = norm_money(m_qty.group(4)[1:])
            items.append(LineItem(description=desc, unit_price=unit, quantity=qty, amount=amt))
            continue

        m_amt = re.search(r"^(.*?)[\s:,-]+(₹\s*[\d,]+)$", line)
        if m_amt:
            desc = m_amt.group(1).strip(":- ")
            amt = norm_money(m_amt.group(2).replace("₹", ""))
            items.append(LineItem(description=desc, amount=amt))
            continue

        m = re.findall(AMOUNT_RE, line)
        if m:
            last_amt = norm_money(m[-1][1])
            desc = re.sub(AMOUNT_RE, "", line).strip(":- ")
            items.append(LineItem(description=desc, amount=last_amt))

    return items

def extract_totals(text: str) -> Dict[str, float]:
    totals = {}

    def find(label, key):
        m = re.search(rf"{label}.*?(₹[\d,]+)", text, re.I | re.DOTALL)
        if m:
            totals[key] = norm_money(m.group(1).replace("₹", ""))

    find("Total Amount", "total_amount")
    find("Discount", "discount")
    find("CGST", "CGST")
    find("SGST", "SGST")
    find("IGST", "IGST")
    find("Total Tax", "total_tax")
    find("Grand Total", "grand_total")
    find("Round Off", "round_off")
    find("Final Amount", "final_amount_printed")

    return totals
