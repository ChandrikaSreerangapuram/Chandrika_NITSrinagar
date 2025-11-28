import os
from pdf2image import convert_from_bytes
from PIL import Image

def load_pages(file_bytes, filename):
    ext = os.path.splitext(filename)[1].lower()
    if ext == ".pdf":
        return convert_from_bytes(file_bytes, dpi=300)
    elif ext in [".png", ".jpg", ".jpeg", ".tif"]:
        return [Image.open(io.BytesIO(file_bytes))]
    else:
        raise ValueError(f"Unsupported file type: {ext}")
