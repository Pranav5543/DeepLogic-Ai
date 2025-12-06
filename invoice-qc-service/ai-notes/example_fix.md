# Example Fix: Date Parsing

## Initial Approach
Initially, the AI (me) considered using a simple regex `\d{2}/\d{2}/\d{4}` for date extraction.

## The Problem
Invoices come in many formats: `Jan 1, 2023`, `2023-01-01`, `01/01/23`. A simple regex would miss many valid dates, leading to "Missing Date" validation errors.

## The Fix
I switched to using `dateutil.parser` which is much more robust. I also updated the regex to capture a wider variety of date strings before passing them to the parser.

```python
# Before
date_match = re.search(r'\d{2}/\d{2}/\d{4}', text)

# After
date_match = re.search(r'Date[:\s]*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\w+\s\d{1,2},?\s\d{4})', text, re.IGNORECASE)
parsed_date = parser.parse(date_match.group(1))
```

This significantly improved the extraction rate on sample invoices.
