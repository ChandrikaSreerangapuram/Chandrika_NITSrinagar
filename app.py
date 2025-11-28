from fastapi import FastAPI, HTTPException, UploadFile, File
from pydantic import BaseModel
import requests
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import re
import uuid
import time

app = FastAPI(
    title="HackRx Bill Extraction API",
    version="1.0.0",
    description="Extract line items, subtotal, totals from bills as per HackRx JSON format"
)

# ------------------------------------
# OCR for an image
# ------------------------------------
def ocr_image(img: Image.Image):
    return pytesseract.image_to_string(img)

# ------------------------------------
# Extract line items from text
# ------------------------------------
def extract_items(text):
    pattern = r"([A-Za-z0-9\/\-\(\) ]+)\s+(\d+(?:\.\d+)?)\s+([\d,.]+)\s+([\d,.]+)"
    items = []

    for match in re.findall(pattern, text):
        name = match[0].strip()
        qty = float(match[1])
        rate = float(match[2].replace(",", ""))
        amount = float(match[3].replace(",", ""))

        items.append({
            "item_name": name,
            "item_quantity": qty,
            "item_rate": rate,
            "item_amount": amount
        })

    return items


# ------------------------------------
# Determine page type
# ------------------------------------
def detect_page_type(text):
    text_lower = text.lower()

    if "pharmacy" in text_lower or "drug" in text_lower or "medicine" in text_lower:
        return "Pharmacy"

    if "total" in text_lower and "final" in text_lower:
        return "Final Bill"

    return "Bill Detail"


# ------------------------------------
# Input JSON Schema
# ------------------------------------
class RequestBody(BaseModel):
    document: str   # URL of bill


# ------------------------------------
# Main API Endpoint Required by HackRx
# ------------------------------------
@app.post("/extract-bill-data")
async def extract_bill_data(body: RequestBody):

    # Step 1: Download File
    try:
        response = requests.get(body.document)
        content = response.content
    except:
        raise HTTPException(status_code=400, detail="Unable to fetch document")

    pages_text = []
    pagewise_items = []

    # Step 2: PDF or Image?
    if body.document.lower().endswith(".pdf"):
        images = convert_from_bytes(content)
    else:
        img = Image.open(io.BytesIO(content))
        images = [img]

    total_token_in = 0
    total_token_out = 0

    # Step 3: Process each page
    for idx, img in enumerate(images):
        text = ocr_image(img)
        pages_text.append(text)

        items = extract_items(text)

        page_type = detect_page_type(text)

        pagewise_items.append({
            "page_no": str(idx + 1),
            "page_type": page_type,
            "bill_items": items
        })

    # Step 4: Total item count
    total_items = sum(len(p["bill_items"]) for p in pagewise_items)

    # Token usage (dummy since no LLM used)
    token_usage = {
        "total_tokens": total_token_in + total_token_out,
        "input_tokens": total_token_in,
        "output_tokens": total_token_out
    }

    # Final Response
    return {
        "is_success": True,
        "token_usage": token_usage,
        "data": {
            "pagewise_line_items": pagewise_items,
            "total_item_count": total_items
        }
    }


@app.get("/")
def root():
    return {"message": "HackRx Bill Extraction API is running"}
