# Invoice OCR & Matching System

This project automates invoice processing for SMEs. It extracts key fields from scanned PDF invoices using pdfplumber and Tesseract OCR, validates them against purchase orders or ledger entries, and flags duplicates or mismatches.

## Features

- Parse PDF invoices and extract invoice number, vendor name, date and total amount.
- Use regex patterns and OCR to handle common invoice layouts.
- Cross-check extracted details against purchase order CSVs or a database.
- Output CSV report with matched/unmatched invoices for audit.
- Modular design for integration into larger accounting workflows.
