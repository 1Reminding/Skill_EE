---
name: pdf
description: Comprehensive PDF manipulation toolkit for extracting text and tables, creating new PDFs, merging/splitting documents, and handling forms.
license: Proprietary
---

# PDF Processing Guide

## Capability and use cases
- **Extraction**: Text and structured table data recovery from digital and scanned PDFs.
- **Manipulation**: Merging, splitting, rotating, and watermarking documents.
- **Generation**: Programmatic PDF creation using canvas or template-based flows.
- **Security**: Password encryption and decryption.
- **OCR**: Converting scanned images to searchable text.

## Required artifacts
- **Python**: `pypdf`, `pdfplumber`, `reportlab`, `pandas`, `pytesseract`, `pdf2image`.
- **System**: `poppler-utils` (pdftotext, pdfimages), `qpdf`, `tesseract-ocr`.

## API/tool patterns

### pypdf: Manipulation
```python
from pypdf import PdfReader, PdfWriter

# Merge
writer = PdfWriter()
for f in ["1.pdf", "2.pdf"]: 
    for p in PdfReader(f).pages: writer.add_page(p)
with open("out.pdf", "wb") as f: writer.write(f)

# Rotate & Encrypt
reader = PdfReader("in.pdf")
writer = PdfWriter()
page = reader.pages[0]
page.rotate(90)
writer.add_page(page)
writer.encrypt("user_pass", "owner_pass")
```

### pdfplumber: Data Extraction
```python
import pdfplumber
import pandas as pd

with pdfplumber.open("doc.pdf") as pdf:
    # Text
    text = "\n".join([p.extract_text() for p in pdf.pages])
    # Tables to DataFrame
    tables = [pd.DataFrame(t[1:], columns=t[0]) for p in pdf.pages for t in p.extract_tables() if t]
```

### reportlab: Generation
```python
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, PageBreak
from reportlab.lib.styles import getSampleStyleSheet

doc = SimpleDocTemplate("out.pdf", pagesize=letter)
story = [Paragraph("Title", getSampleStyleSheet()['Title']), PageBreak()]
doc.build(story)
```

### CLI Tools
```bash
# Text extraction with layout
pdftotext -layout input.pdf output.txt

# qpdf: Merge and Decrypt
qpdf --empty --pages f1.pdf f2.pdf -- merged.pdf
qpdf --password=pw --decrypt in.pdf out.pdf

# Extract images
pdfimages -j input.pdf img_prefix
```

## Implementation anchors
- `pypdf.PdfReader(path).metadata`: Access title, author, creator.
- `page.merge_page(watermark_page)`: Apply watermarks.
- `pdf2image.convert_from_path(path)`: Convert PDF to PIL images for OCR.
- `pytesseract.image_to_string(image)`: Perform OCR on converted images.

## Workflow
1. **Ingestion**: Open file via `PdfReader` or `pdfplumber.open`.
2. **Transformation**: Iterate through `pages`; apply `rotate()`, `merge_page()`, or `add_page()` to a `PdfWriter` instance.
3. **Extraction**: Use `extract_tables()` for structured data or `pdftotext -layout` for columned text.
4. **Output**: Finalize via `writer.write()`, `canvas.save()`, or `doc.build()`.

## Validation checks
- Verify `len(reader.pages)` matches expected document length.
- Check `if table:` before attempting `pd.DataFrame` construction to avoid empty list errors.
- Ensure `poppler-utils` is in system PATH for `pdf2image` and `pdftotext`.

## Pitfalls
- **Scanned PDFs**: Standard extraction returns empty strings; requires `pytesseract` OCR.
- **Layout**: Default text extraction may merge columns; use `pdfplumber` or `pdftotext -layout` for better spatial fidelity.
- **Encryption**: Some PDFs require decryption via `qpdf` before processing with `pypdf`.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
import pandas as pd

with pdfplumber.open("document.pdf") as pdf:
    all_tables = []
    for page in pdf.pages:
        tables = page.extract_tables()
        for table in tables:
            if table:  # Check if table is not empty
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

# Combine all tables
if all_tables:
    combined_df = pd.concat(all_tables, ignore_index=True)
    combined_df.to_excel("extracted_tables.xlsx", index=False)
```
### Anchor 2
```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```
