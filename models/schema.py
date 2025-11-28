from typing import List, Optional, Dict
from pydantic import BaseModel

class LineItem(BaseModel):
    description: str
    unit_price: Optional[float] = None
    quantity: Optional[float] = None
    amount: float

class Taxes(BaseModel):
    details: Dict[str, float]
    total_tax: Optional[float] = None

class InvoiceOutput(BaseModel):
    bill_no: Optional[str]
    bill_date: Optional[str]
    patient_name: Optional[str]
    line_items: List[LineItem]
    sub_totals: List[Dict[str, float]]
    discount: Optional[float]
    taxes: Optional[Taxes]
    grand_total: Optional[float]
    round_off: Optional[float]
    final_total: float
    meta: Dict[str, str]
    anomalies: List[str]
