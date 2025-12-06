import pdfplumber
import re
import os
from datetime import datetime
from typing import List, Optional
from .schema import Invoice, LineItem
from dateutil import parser

def parse_date(date_str: str) -> Optional[datetime.date]:
    if not date_str:
        return None
    try:
        return parser.parse(date_str).date()
    except:
        return None

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def extract_invoice_from_pdf(pdf_path: str) -> Invoice:
    filename = os.path.basename(pdf_path)
    text = extract_text_from_pdf(pdf_path)
    
    # Heuristics & Regex
    invoice_number_match = re.search(r'Invoice\s*(?:No|Number|#)?[:\s]*([A-Za-z0-9\-]+)', text, re.IGNORECASE)
    invoice_date_match = re.search(r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s\d{1,2},?\s\d{4})', text, re.IGNORECASE)
    
    # Totals
    # Look for patterns like "Total: 1,234.56"
    gross_total_match = re.search(r'(?:Gross\s*)?Total[:\s]*[$€£]?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)
    net_total_match = re.search(r'(?:Net|Sub)\s*Total[:\s]*[$€£]?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)
    tax_match = re.search(r'Tax[:\s]*[$€£]?\s*([\d,]+\.\d{2})', text, re.IGNORECASE)

    # Helper to clean float strings
    def clean_float(s):
        if not s: return 0.0
        return float(s.replace(',', ''))

    invoice_number = invoice_number_match.group(1) if invoice_number_match else None
    invoice_date = parse_date(invoice_date_match.group(1)) if invoice_date_match else None
    
    gross_total = clean_float(gross_total_match.group(1)) if gross_total_match else 0.0
    net_total = clean_float(net_total_match.group(1)) if net_total_match else 0.0
    tax_amount = clean_float(tax_match.group(1)) if tax_match else 0.0
    
    # Fallback: if net is 0 but gross and tax exist
    if net_total == 0.0 and gross_total > 0:
        net_total = gross_total - tax_amount

    # Currency (Simple heuristic)
    currency = "USD"
    if "EUR" in text or "€" in text: currency = "EUR"
    elif "GBP" in text or "£" in text: currency = "GBP"
    elif "INR" in text or "₹" in text: currency = "INR"

    # Entities (Very basic heuristic - usually top left is seller, below is buyer)
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    seller_name = lines[0] if lines else None
    buyer_name = None
    # Try to find "Bill To"
    for i, line in enumerate(lines):
        if "Bill To" in line or "Ship To" in line:
            if i + 1 < len(lines):
                buyer_name = lines[i+1]
            break
            
    # Line Items extraction (Simplified for assignment)
    # In a real world, we'd use pdfplumber.extract_table()
    line_items = []
    # Attempt to find table data
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                for row in table:
                    # Heuristic: Row has number, description, price
                    # Filter out header rows
                    if not row or "Description" in str(row[0]) or "Qty" in str(row):
                        continue
                    
                    # Try to map columns. Assuming standard: Desc, Qty, Unit, Total
                    # This is highly variable, so we'll do a best effort mapping
                    # If row has >= 3 elements
                    cleaned_row = [c for c in row if c]
                    if len(cleaned_row) >= 3:
                        try:
                            # Assume last is total, second last is price, third last is qty?
                            # Or: Desc, Qty, Price, Total
                            # Let's try to find numbers
                            nums = []
                            desc = ""
                            for cell in cleaned_row:
                                try:
                                    val = float(cell.replace(',', '').replace('$', ''))
                                    nums.append(val)
                                except:
                                    desc += " " + str(cell)
                            
                            if len(nums) >= 3:
                                qty = nums[0]
                                unit = nums[1]
                                total = nums[-1]
                                line_items.append(LineItem(
                                    description=desc.strip(),
                                    quantity=qty,
                                    unit_price=unit,
                                    line_total=total
                                ))
                        except:
                            pass

    return Invoice(
        invoice_id=filename,
        invoice_number=invoice_number,
        invoice_date=invoice_date,
        seller_name=seller_name,
        buyer_name=buyer_name,
        currency=currency,
        net_total=net_total,
        tax_amount=tax_amount,
        gross_total=gross_total,
        line_items=line_items,
        source_file=pdf_path
    )
