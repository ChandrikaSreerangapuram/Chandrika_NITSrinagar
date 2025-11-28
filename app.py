import io
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from models.schema import InvoiceOutput
from services.preprocess import preprocess_image
from services.ocr import ocr_pages
from services.parser import extract_header_fields, parse_line_items, extract_totals
from services.fraud import image_anomalies
from services.reconcile import (
    deduplicate_items, compute_subtotals, sum_items,
    compute_final_total, build_taxes_dict
)
from utils.files import load_pages
from utils.math import approx_equal

app = FastAPI(title="Invoice Extraction API")

@app.post("/extract", response_model=InvoiceOutput)
async def extract(file: UploadFile = File(...), lang: str = "eng"):
    file_bytes = await file.read()
    pages = load_pages(file_bytes, file.filename)

    preprocessed = [preprocess_image(p) for p in pages]
    anomalies = []

    for p in preprocessed:
        anomalies.extend(image_anomalies(p))

    text = ocr_pages(preprocessed, lang=lang)

    headers = extract_header_fields(text)
    items = deduplicate_items(parse_line_items(text))
    totals_map = extract_totals(text)
    sub_totals = compute_subtotals(text, items)
    taxes = build_taxes_dict(totals_map)

    discount = totals_map.get("discount", 0.0)
    printed_grand = totals_map.get("grand_total")
    round_off = totals_map.get("round_off", 0.0)
    printed_final = totals_map.get("final_amount_printed")

    items_sum = sum_items(items)
    taxes_total = taxes.total_tax or 0.0
    final_total = compute_final_total(items_sum, discount, taxes_total, round_off, printed_final)

    if printed_final and not approx_equal(printed_final, final_total, eps=1.0):
        anomalies.append("Computed final total differs significantly from printed final amount.")

    meta = {
        "items_sum": str(items_sum),
        "discount": str(discount),
        "taxes_total": str(taxes_total),
        "round_off": str(round_off),
        "printed_grand_total": str(printed_grand),
        "printed_final_amount": str(printed_final or final_total)
    }

    return InvoiceOutput(
        bill_no=headers.get("bill_no"),
        bill_date=headers.get("bill_date"),
        patient_name=headers.get("patient_name"),
        line_items=items,
        sub_totals=sub_totals,
        discount=discount,
        taxes=taxes,
        grand_total=printed_grand,
        round_off=round_off,
        final_total=final_total,
        meta=meta,
        anomalies=anomalies
    )
