import pandas as pd
import pdfplumber
import pytesseract
from PIL import Image
import re

# Configure Tesseract path if needed (Windows example)
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

def load_invoice_dfs(uploaded_file):
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
        return df, pd.DataFrame(), None
    elif uploaded_file.name.endswith(".xlsx"):
        df = pd.read_excel(uploaded_file)
        return df, pd.DataFrame(), None
    elif uploaded_file.name.endswith(".pdf"):
        return parse_pdf(uploaded_file)
    else:
        raise ValueError("Unsupported file format. Please upload CSV, XLSX, or PDF.")

def parse_pdf(uploaded_file):
    text = ""
    with pdfplumber.open(uploaded_file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
            else:
                img = page.to_image(resolution=300).original
                text += pytesseract.image_to_string(img) + "\n"

    # Regex patterns
    freight_bill_pattern = re.compile(r"Freight\s*Bill\s*(?:No\.?|Number)\s*(\d+)", re.IGNORECASE)
    total_due_pattern = re.compile(r"Total\s*Amount\s*Due\s*([\d,]+\.\d{2})", re.IGNORECASE)
    line_item_pattern = re.compile(r"([A-Za-z0-9\-\/&\s]+)\s+([\d,]+\.\d{2})")
    accessorial_pattern = re.compile(r"(Fuel Surcharge|FUEL SURCHG|Liftgate|REDELIVERY CHARGE|CORRECTION FEE)\s+([\d,]+\.\d{2})", re.IGNORECASE)

    # Extract Freight Bill Number
    freight_bill_match = freight_bill_pattern.search(text)
    freight_bill_number = freight_bill_match.group(1) if freight_bill_match else "Unknown"

    # Extract Total Amount Due
    total_due_match = total_due_pattern.search(text)
    total_amount_due = float(total_due_match.group(1).replace(",", "")) if total_due_match else 0.0

    # Extract line items
    line_items = []
    for desc, amount in line_item_pattern.findall(text):
        line_items.append({
            "freight_bill_number": freight_bill_number,
            "type": desc.strip(),
            "billed_amount": float(amount.replace(",", ""))
        })

    # Extract accessorials
    accessorials = []
    for desc, amount in accessorial_pattern.findall(text):
        accessorials.append({
            "freight_bill_number": freight_bill_number,
            "type": desc.strip(),
            "billed_amount": float(amount.replace(",", ""))
        })

    line_items_df = pd.DataFrame(line_items)
    accessorials_df = pd.DataFrame(accessorials)

    return line_items_df, accessorials_df, total_amount_due