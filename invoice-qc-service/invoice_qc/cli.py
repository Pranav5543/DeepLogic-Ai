import typer
import json
import os
from typing import Optional
from .extractor import extract_invoice_from_pdf
from .validator import validate_batch
from .schema import Invoice

app = typer.Typer()

@app.command()
def extract(pdf_dir: str, output: str = "extracted.json"):
    """Extract invoices from a directory of PDFs."""
    invoices = []
    if not os.path.exists(pdf_dir):
        typer.echo(f"Directory {pdf_dir} not found!")
        raise typer.Exit(code=1)

    files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    with typer.progressbar(files, label="Extracting") as progress:
        for f in progress:
            path = os.path.join(pdf_dir, f)
            try:
                inv = extract_invoice_from_pdf(path)
                invoices.append(inv.dict())
            except Exception as e:
                typer.echo(f"Failed to extract {f}: {e}")

    # Convert date objects to string for JSON
    with open(output, 'w') as f:
        json.dump(invoices, f, default=str, indent=2)
    
    typer.echo(f"Extracted {len(invoices)} invoices to {output}")

@app.command()
def validate(input: str, report: str = "validation_report.json"):
    """Validate extracted invoices from a JSON file."""
    if not os.path.exists(input):
        typer.echo(f"Input file {input} not found!")
        raise typer.Exit(code=1)

    with open(input, 'r') as f:
        data = json.load(f)
    
    # Parse back to objects
    invoices = [Invoice(**d) for d in data]
    
    result = validate_batch(invoices)
    
    with open(report, 'w') as f:
        json.dump(result, f, indent=2)

    summary = result['summary']
    typer.echo("\n--- Validation Summary ---")
    typer.echo(f"Total: {summary['total_invoices']}")
    typer.echo(f"Valid: {summary['valid_invoices']}")
    typer.echo(f"Invalid: {summary['invalid_invoices']}")
    
    if summary['invalid_invoices'] > 0:
        typer.echo("\nTop Errors:")
        for err, count in summary['error_counts'].items():
            typer.echo(f"- {err}: {count}")
        raise typer.Exit(code=1)

@app.command()
def full_run(pdf_dir: str, report: str = "validation_report.json"):
    """Extract and validate in one go."""
    # 1. Extract
    invoices = []
    if not os.path.exists(pdf_dir):
        typer.echo(f"Directory {pdf_dir} not found!")
        raise typer.Exit(code=1)

    files = [f for f in os.listdir(pdf_dir) if f.lower().endswith('.pdf')]
    for f in files:
        path = os.path.join(pdf_dir, f)
        try:
            inv = extract_invoice_from_pdf(path)
            invoices.append(inv)
        except Exception as e:
            typer.echo(f"Failed to extract {f}: {e}")
            
    # 2. Validate
    result = validate_batch(invoices)
    
    with open(report, 'w') as f:
        json.dump(result, f, indent=2)
        
    summary = result['summary']
    typer.echo("\n--- Validation Summary ---")
    typer.echo(f"Total: {summary['total_invoices']}")
    typer.echo(f"Valid: {summary['valid_invoices']}")
    typer.echo(f"Invalid: {summary['invalid_invoices']}")
    
    if summary['invalid_invoices'] > 0:
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()
