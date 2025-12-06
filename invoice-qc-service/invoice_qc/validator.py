from typing import List, Dict
from .schema import Invoice, InvoiceValidationResult, InvoiceValidationError, GlobalValidationSummary
from collections import defaultdict

def validate_invoice(invoice: Invoice, all_invoices: List[Invoice] = []) -> InvoiceValidationResult:
    errors = []

    # 1. Completeness Rules
    if not invoice.invoice_number:
        errors.append(InvoiceValidationError(field="invoice_number", message="Invoice number is missing"))
    
    if not invoice.invoice_date:
        errors.append(InvoiceValidationError(field="invoice_date", message="Invoice date is missing or invalid"))
        
    if not invoice.seller_name:
        errors.append(InvoiceValidationError(field="seller_name", message="Seller name is missing"))
        
    if not invoice.buyer_name:
        errors.append(InvoiceValidationError(field="buyer_name", message="Buyer name is missing"))
        
    if not invoice.currency:
        errors.append(InvoiceValidationError(field="currency", message="Currency is missing"))

    # 2. Business Rules
    # net + tax ~ gross
    calculated_gross = invoice.net_total + invoice.tax_amount
    if abs(calculated_gross - invoice.gross_total) > 0.05: # Tolerance
        errors.append(InvoiceValidationError(
            field="totals", 
            message=f"Net ({invoice.net_total}) + Tax ({invoice.tax_amount}) != Gross ({invoice.gross_total})"
        ))

    # Line items sum ~ net
    if invoice.line_items:
        line_sum = sum(item.line_total for item in invoice.line_items)
        # Sometimes line items sum to gross, sometimes net. Usually net.
        # We'll check against Net first, then Gross if that fails, just to be safe? 
        # Requirement says: sum of all line_items.line_total ≈ net_total
        if abs(line_sum - invoice.net_total) > 0.05:
             errors.append(InvoiceValidationError(
                field="line_items", 
                message=f"Sum of line items ({line_sum}) != Net Total ({invoice.net_total})"
            ))

    # 3. Anomaly/Duplicate Rule
    # Duplicate invoice detection: invoice_number + seller_name + invoice_date
    # We need the context of other invoices.
    for other in all_invoices:
        if other.invoice_id == invoice.invoice_id:
            continue # Skip self
        
        if (other.invoice_number == invoice.invoice_number and 
            other.seller_name == invoice.seller_name and 
            other.invoice_date == invoice.invoice_date):
            errors.append(InvoiceValidationError(
                field="duplicate",
                message=f"Potential duplicate of {other.invoice_id}"
            ))
            break

    return InvoiceValidationResult(
        invoice_id=invoice.invoice_id,
        is_valid=len(errors) == 0,
        errors=errors
    )

def validate_batch(invoices: List[Invoice]) -> Dict:
    results = []
    valid_count = 0
    invalid_count = 0
    error_counts = defaultdict(int)

    for inv in invoices:
        res = validate_invoice(inv, invoices)
        results.append(res)
        if res.is_valid:
            valid_count += 1
        else:
            invalid_count += 1
            for err in res.errors:
                error_counts[err.message] += 1
    
    summary = GlobalValidationSummary(
        total_invoices=len(invoices),
        valid_invoices=valid_count,
        invalid_invoices=invalid_count,
        error_counts=dict(error_counts)
    )

    return {
        "summary": summary.dict(),
        "results": [r.dict() for r in results]
    }
