import pytesseract
from PIL import Image

def run_ocr(img: Image.Image, lang: str = "eng") -> str:
    config = "--psm 6 -c preserve_interword_spaces=1"
    return pytesseract.image_to_string(img, lang=lang, config=config)

def ocr_pages(pages, lang="eng"):
    texts = []
    for p in pages:
        texts.append(run_ocr(p, lang=lang))
    return "\n\n---- PAGE BREAK ----\n\n".join(texts)
