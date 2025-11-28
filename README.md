HackRx Bill Extraction API

Datathon – Bajaj Finserv Health Limited
Submission: Bill Line-Item Extraction & Summarization API

1. Problem Statement

Hospitals submit bills in PNG, JPG, and PDF formats, often multi-page and unstructured.
The task is to build a system that:

Extracts all line items from each page

Extracts item name, quantity, rate, and amount

Identifies page type (Bill Detail, Final Bill, Pharmacy)

Extracts sub-totals (when present) and final total

Ensures no missing line items and no double counting

Outputs data in the required JSON structure

Exposes the extraction as a POST API endpoint

2. Solution Overview

This solution uses:

Tesseract OCR for extracting text from images and PDFs

pdf2image for PDF page conversion

Regular expressions for structured table-like extraction

Rule-based page classification

Aggregation logic for total item count and totals

FastAPI backend deployed on Render

JSON response compliant with the HackRx evaluation system

3. API Endpoint (Submission Link)

POST /extract-bill-data

Example deployment URL (replace with your Render link):

https://your-app-name.onrender.com/extract-bill-data


This is the link to submit for the Datathon.

4. Input Format

Request Body:

{
  "document": "https://example.com/sample_bill.png"
}


(document must be a publicly accessible URL)

5. Output JSON Format
{
  "is_success": true,
  "token_usage": {
    "total_tokens": 0,
    "input_tokens": 0,
    "output_tokens": 0
  },
  "data": {
    "pagewise_line_items": [
      {
        "page_no": "1",
        "page_type": "Bill Detail",
        "bill_items": [
          {
            "item_name": "WARD SERVICES",
            "item_amount": 3000,
            "item_rate": 1500,
            "item_quantity": 2
          }
        ]
      }
    ],
    "total_item_count": 12
  }
}

6. Directory Structure
project/
│-- main.py
│-- requirements.txt
│-- README.md

7. How to Run Locally

Install dependencies:

pip install -r requirements.txt


Start the FastAPI server:

uvicorn main:app --reload


Open interactive API docs:

http://127.0.0.1:8000/docs

8. Deployment on Render

Go to https://render.com

Create a new Web Service

Connect your GitHub repository

Configure:

Runtime: Python 3.10+

Start Command:

uvicorn main:app --host 0.0.0.0 --port 10000


Deploy

Your submission endpoint will look like:

https://your-app.onrender.com/extract-bill-data


This is the link you must submit.

9. Features

Supports PDF, JPG, PNG, multi-page documents

OCR and rule-based extraction

Page type detection

No duplicate item counting

Accurate total calculation

Fully compliant JSON output

Lightweight and fast API

10. Future Enhancements

Integration with LLMs for high-accuracy structured extraction

Table detection models

Fraud detection (font inconsistencies, overwriting detection)

Layout-aware document parsing models