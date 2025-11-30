from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
import requests
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import io
import re

app = FastAPI(
    title="HackRx Bill Extraction API",
    version="1.1.0",
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
    # Preprocess text: replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    # Regex pattern: item name, quantity, rate, amount
    pattern = r"([A-Za-z0-9\/\-\(\) ]+?)\s+(\d+(?:\.\d+)?)\s+([\d,.]+)\s+([\d,.]+)"
    items = []

    for match in re.findall(pattern, text):
        try:
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
        except:
            continue

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
# Input JSON Schema for URL
# ------------------------------------
class RequestBody(BaseModel):
    document: str   # URL of bill

# ------------------------------------
# Main API Endpoint
# ------------------------------------
@app.post("/extract_bill_data")
async def extract_bill_data(
    body: RequestBody = None,
    file: UploadFile = File(None)
):
    # Step 1: Fetch document content
    content = None
    if file:
        content = await file.read()
    elif body and body.document:
        try:
            response = requests.get(body.document)
            response.raise_for_status()
            content = response.content
        except requests.exceptions.RequestException:
            raise HTTPException(status_code=400, detail="Unable to fetch document from URL")
    else:
        raise HTTPException(status_code=400, detail="No document provided")

    # Step 2: Determine PDF or Image
    images = []
    if file and file.filename.lower().endswith(".pdf") or (body and body.document.lower().endswith(".pdf")):
        images = convert_from_bytes(content)
    else:
        img = Image.open(io.BytesIO(content))
        images = [img]

    pagewise_items = []

    # Step 3: Process each page
    for idx, img in enumerate(images):
        text = ocr_image(img)
        items = extract_items(text)
        page_type = detect_page_type(text)

        pagewise_items.append({
            "page_no": str(idx + 1),
            "page_type": page_type,
            "bill_items": items
        })

    # Step 4: Total item count
    total_items = sum(len(p["bill_items"]) for p in pagewise_items)

    # Token usage placeholder (no LLM used)
    token_usage = {
        "total_tokens": 0,
        "input_tokens": 0,
        "output_tokens": 0
    }

    # Final response
    return {
        "is_success": True,
        "token_usage": token_usage,
        "data": {
            "pagewise_line_items": pagewise_items,
            "total_item_count": total_items
        }
    }

# ------------------------------------
# Root endpoint
# ------------------------------------
@app.get("/")
def root():
    return {"message": "HackRx Bill Extraction API is running"}
