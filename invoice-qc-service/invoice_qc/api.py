from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import shutil
import os
import tempfile
from .schema import Invoice
from .validator import validate_batch
from .extractor import extract_invoice_from_pdf

app = FastAPI(title="Invoice QC Service")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {
        "message": "Welcome to Invoice QC Service API",
        "docs": "/docs",
        "health": "/health"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/validate-json")
def validate_json_endpoint(invoices: List[Invoice]):
    return validate_batch(invoices)

@app.post("/extract-and-validate-pdfs")
async def extract_and_validate(files: List[UploadFile] = File(...)):
    invoices = []
    
    # Create a temp dir to save files (pdfplumber needs path)
    with tempfile.TemporaryDirectory() as temp_dir:
        for file in files:
            temp_path = os.path.join(temp_dir, file.filename)
            with open(temp_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            try:
                inv = extract_invoice_from_pdf(temp_path)
                # Reset source file to just filename for cleaner output
                inv.source_file = file.filename 
                invoices.append(inv)
            except Exception as e:
                # In a real app, we might handle this better
                print(f"Error processing {file.filename}: {e}")

    return validate_batch(invoices)
