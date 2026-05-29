---
name: pdf
description: "ALWAYS use this skill instead of the Read tool for PDF files. The Read tool cannot extract PDF tables properly. Use for: (1) Reading ANY PDF, (2) Table extraction, (3) PDF to pandas conversion, (4) Multi-page processing."
---

# PDF Processing with pdfplumber

## Capability and use cases
- High-fidelity extraction of text and tabular data from PDF files.
- Conversion of PDF tables into structured pandas DataFrames.
- Processing multi-page documents where tables span across pages.

## Required artifacts
- `pdfplumber` (primary extraction library)
- `pandas` (data manipulation)

## API/tool patterns
- `pdfplumber.open("path.pdf")`: Context manager for PDF access.
- `page.extract_tables()`: Returns list of tables (list of lists).
- `page.extract_text(layout=True)`: Returns text preserving visual layout.

## Implementation anchors
```python
import pdfplumber
import pandas as pd

# Table to DataFrame
with pdfplumber.open("doc.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]
    df = pd.DataFrame(table[1:], columns=table[0])

# Multi-page Table Accumulation
all_dfs = []
with pdfplumber.open("doc.pdf") as pdf:
    for page in pdf.pages:
        for tbl in page.extract_tables():
            if tbl and len(tbl) > 1:
                all_dfs.append(pd.DataFrame(tbl[1:], columns=tbl[0]))
combined_df = pd.concat(all_dfs, ignore_index=True)

# Data Cleaning
df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x).dropna(how='all')
```

## Workflow
1. **Open**: Use `pdfplumber.open()` to initialize the file.
2. **Iterate**: Loop through `pdf.pages` to ensure no data is missed.
3. **Extract**: Call `extract_tables()` for data or `extract_text()` for prose.
4. **Identify**: Check headers (e.g., `if 'ID' in header`) to distinguish table types or continuation pages.
5. **Clean**: Strip whitespace from cells and column names; drop empty rows.

## Validation checks
- Verify `table` is not None and `len(table) > 1` before slicing headers.
- Check if expected column names exist in `table[0]` to handle missing headers.
- Use `try-except` blocks for type casting (e.g., `int(row[0])`) to handle extraction noise.

## Pitfalls
- **CRITICAL**: Do NOT use the Read tool; it provides only a limited text preview and misses tables.
- **Scanned PDFs**: `pdfplumber` fails on image-based PDFs; requires OCR (e.g., `pytesseract`).
- **Merged Cells**: May cause misaligned columns in the extracted list of lists.
- **Continuation Pages**: Tables spanning pages often lack headers on subsequent pages; use positional indexing.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    table = pdf.pages[0].extract_tables()[0]
    df = pd.DataFrame(table[1:], columns=table[0])

    # Clean whitespace
    df = df.apply(lambda x: x.str.strip() if x.dtype == "object" else x)

    # Remove empty rows
    df = df.dropna(how='all')

    # Rename columns if needed
    df.columns = df.columns.str.strip()
```
### Anchor 2
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]  # First page
    tables = page.extract_tables()

    if tables:
        # First row is usually headers
        table = tables[0]
        df = pd.DataFrame(table[1:], columns=table[0])
        print(df)
```
