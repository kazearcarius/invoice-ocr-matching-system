"""
Invoice OCR & Matching System
=============================

This script demonstrates a simple workflow for processing scanned invoice PDFs.
It extracts key fields using OCR and pdf parsing libraries, then matches the
results against existing purchase orders or ledger entries stored in a CSV.

Due to the complexity of production‑grade OCR, this example focuses on the
overall flow. In practice you would tune OCR settings, handle different
document layouts and integrate with your accounting system.

Dependencies:
    pandas, pdfplumber, pytesseract, Pillow
"""

import argparse
import os
import re
from typing import Dict, List, Optional

import pandas as pd
import pdfplumber

try:
    import pytesseract  # type: ignore
    from PIL import Image
except ImportError:
    pytesseract = None  # OCR optional; script will degrade gracefully
    Image = None


def extract_text_from_pdf(path: str) -> str:
    """Extract raw text from a PDF using pdfplumber."""
    text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text.append(page.extract_text() or "")
    return "\n".join(text)


def extract_fields(text: str) -> Dict[str, Optional[str]]:
    """Extract key invoice fields using simple regex patterns."""
    fields = {
        'invoice_number': None,
        'vendor': None,
        'date': None,
        'total': None,
    }
    # Example patterns – real patterns would need to handle many formats
    num_match = re.search(r"Invoice\s*#?\s*(\w+)", text, re.IGNORECASE)
    if num_match:
        fields['invoice_number'] = num_match.group(1)
    total_match = re.search(r"Total\s*[:\-]?\s*([\d,.]+)", text, re.IGNORECASE)
    if total_match:
        fields['total'] = total_match.group(1)
    return fields


def match_against_po(fields: Dict[str, Optional[str]], purchase_orders: pd.DataFrame) -> bool:
    """Return True if the invoice matches a purchase order in the DataFrame."""
    if not fields['invoice_number']:
        return False
    return fields['invoice_number'] in purchase_orders['InvoiceNumber'].values


def process_invoices(pdf_folder: str, po_csv: str, output_csv: str) -> None:
    """Process all PDFs in a folder and match them against a purchase order file."""
    purchase_orders = pd.read_csv(po_csv)
    results = []
    for fname in os.listdir(pdf_folder):
        if not fname.lower().endswith('.pdf'):
            continue
        path = os.path.join(pdf_folder, fname)
        text = extract_text_from_pdf(path)
        fields = extract_fields(text)
        matched = match_against_po(fields, purchase_orders)
        fields['file'] = fname
        fields['matched'] = matched
        results.append(fields)
    pd.DataFrame(results).to_csv(output_csv, index=False)
    print(f"Processed {len(results)} invoices; results saved to {output_csv}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Extract and match invoices against purchase orders.")
    parser.add_argument("--pdf-folder", required=True, help="Folder containing invoice PDFs")
    parser.add_argument("--po-csv", required=True, help="CSV file with purchase orders (must include InvoiceNumber column)")
    parser.add_argument("--output", required=True, help="Path to save the results CSV")
    args = parser.parse_args()

    process_invoices(args.pdf_folder, args.po_csv, args.output)


if __name__ == '__main__':
    main()