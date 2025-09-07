# app/models.py
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io

def extract_text_from_pdf(path: str, ocr_if_empty: bool = True) -> tuple[str, bool]:
    """
    Extracts text from a PDF file.

    Returns:
        tuple[text, used_ocr_flag]
        - text: the extracted text
        - used_ocr_flag: True if OCR was used, False otherwise
    """
    text = ""
    doc = fitz.open(path)

    # Extract text normally
    for page in doc:
        txt = page.get_text()
        if txt:
            text += txt + "\n"

    used_ocr = False

    # If no text and OCR is enabled, render pages and perform OCR
    if ocr_if_empty and not text.strip():
        used_ocr = True
        for i in range(len(doc)):
            pix = doc[i].get_pixmap(dpi=200)
            img = Image.open(io.BytesIO(pix.tobytes()))
            page_text = pytesseract.image_to_string(img)
            if page_text:
                text += page_text + "\n"

    return text, used_ocr
