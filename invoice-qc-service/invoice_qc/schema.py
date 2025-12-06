from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from datetime import date
import re

class LineItem(BaseModel):
    description: str
    quantity: float
    unit_price: float
    line_total: float

class Invoice(BaseModel):
    invoice_id: str = Field(..., description="Unique ID for the invoice (e.g. filename or internal ID)")
    invoice_number: Optional[str] = None
    external_reference: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    seller_name: Optional[str] = None
    seller_tax_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    currency: Optional[str] = Field(None, min_length=3, max_length=3)
    net_total: float = 0.0
    tax_amount: float = 0.0
    gross_total: float = 0.0
    payment_terms: Optional[str] = None
    line_items: List[LineItem] = []
    source_file: str

    @field_validator('currency')
    @classmethod
    def validate_currency(cls, v):
        if v and not re.match(r'^[A-Z]{3}$', v):
            raise ValueError('Currency must be a valid 3-letter ISO code')
        return v

class InvoiceValidationError(BaseModel):
    field: str
    message: str

class InvoiceValidationResult(BaseModel):
    invoice_id: str
    is_valid: bool
    errors: List[InvoiceValidationError]

class GlobalValidationSummary(BaseModel):
    total_invoices: int
    valid_invoices: int
    invalid_invoices: int
    error_counts: dict
