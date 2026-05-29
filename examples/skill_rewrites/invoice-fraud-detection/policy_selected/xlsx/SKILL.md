---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and visualization. Use for: (1) Creating spreadsheets with formulas/formatting, (2) Data analysis, (3) Modifying existing files while preserving formulas, (4) Visualization, (5) Recalculating formulas."
license: Proprietary. LICENSE.txt has complete terms
---

# Capability and use cases
Supports .xlsx, .xlsm, .csv, and .tsv files. Primary capabilities include programmatic spreadsheet generation with dynamic formulas, financial modeling following industry standards, and automated formula recalculation via LibreOffice integration.

# Required artifacts
- **Python Libraries**: `pandas`, `openpyxl`
- **Recalculation Engine**: `recalc.py` (requires LibreOffice)

# API/tool patterns

### Data Analysis (pandas)
```python
import pandas as pd
df = pd.read_excel('file.xlsx', sheet_name=None) # Load all sheets
# Analysis: df.describe(), df.info()
df.to_excel('output.xlsx', index=False)
```

### Formulas and Formatting (openpyxl)
```python
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Header'
sheet['B2'] = '=SUM(A1:A10)' # Use strings for formulas
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
wb.save('output.xlsx')
```

### Recalculation Command
```bash
python recalc.py output.xlsx 30
```

# Implementation anchors

### Financial Model Standards
- **Blue (0,0,255)**: Hardcoded inputs/scenarios
- **Black (0,0,0)**: Formulas and calculations
- **Green (0,128,0)**: Internal worksheet links
- **Red (255,0,0)**: External file links
- **Yellow BG (255,255,0)**: Key assumptions/cells requiring attention

### Number Formatting
- **Currency**: `$#,##0;($#,##0);-` (Specify units in headers like "Revenue ($mm)")
- **Years**: Text strings (e.g., "2024")
- **Percentages**: `0.0%`
- **Multiples**: `0.0x`
- **Negatives**: Parentheses `(123)`

### Formula Logic
- **No Hardcoding**: Use `=B5*(1+$B$6)` instead of `=B5*1.05`.
- **Documentation**: Hardcodes require source comments: `Source: [System], [Date], [Reference], [URL]`.

# Workflow
1. **Initialize**: Load existing file via `load_workbook()` or create new `Workbook()`.
2. **Modify**: Apply data and formulas. Use `openpyxl` to preserve existing formatting.
3. **Save**: Write to disk.
4. **Recalculate**: Execute `python recalc.py <file>`. This is MANDATORY for files with formulas.
5. **Verify**: Inspect the JSON output from `recalc.py` for `errors_found`.

# Validation checks
- **Zero Error Tolerance**: No `#REF!`, `#DIV/0!`, `#VALUE!`, `#N/A`, or `#NAME?`.
- **Recalc Output**: 
  ```json
  { "status": "success", "total_errors": 0, "total_formulas": 42 }
  ```
- **Index Check**: Excel is 1-indexed (DataFrame row 5 = Excel row 6).
- **Column Mapping**: Verify high-index columns (e.g., Col 64 = BL).

# Pitfalls
- **Data Loss**: Opening with `load_workbook(data_only=True)` and saving will permanently delete formulas.
- **Python Hardcoding**: Do not calculate values in Python and write the result; write the Excel formula string instead.
- **NaN Values**: Use `pd.notna()` to handle nulls before processing.
- **LibreOffice**: Recalculation will fail if LibreOffice is not accessible to `recalc.py`.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
# Using openpyxl to preserve formulas and formatting
from openpyxl import load_workbook

# Load existing file
wb = load_workbook('existing.xlsx')
sheet = wb.active  # or wb['SheetName'] for specific sheet

# Working with multiple sheets
for sheet_name in wb.sheetnames:
    sheet = wb[sheet_name]
    print(f"Sheet: {sheet_name}")

# Modify cells
sheet['A1'] = 'New Value'
sheet.insert_rows(2)  # Insert row at position 2
sheet.delete_cols(3)  # Delete column 3

# Add new sheet
new_sheet = wb.create_sheet('NewSheet')
new_sheet['A1'] = 'Data'

wb.save('modified.xlsx')
```
### Anchor 2
```python
# Using openpyxl for formulas and formatting
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active

# Add data
sheet['A1'] = 'Hello'
sheet['B1'] = 'World'
sheet.append(['Row', 'of', 'data'])

# Add formula
sheet['B2'] = '=SUM(A1:A10)'

# Formatting
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')

# Column width
sheet.column_dimensions['A'].width = 20

wb.save('output.xlsx')
```
