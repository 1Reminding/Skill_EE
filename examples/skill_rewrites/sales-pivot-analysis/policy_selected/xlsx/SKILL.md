---
name: xlsx
description: "Comprehensive spreadsheet creation, editing, and analysis with support for formulas, formatting, data analysis, and pivot tables."
---

# XLSX Creation, Editing, and Analysis

## Capability and use cases
- Creating/editing .xlsx files with formatting and formulas.
- Data analysis using pandas.
- Programmatic pivot table generation via openpyxl.
- Building multi-sheet workbooks with source data and summary sheets.

## Required artifacts
- `pandas`: For data manipulation and analysis.
- `openpyxl`: For Excel-specific features (styles, pivot tables).

## API/tool patterns
```python
import pandas as pd
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems

# Read: df = pd.read_excel('f.xlsx', sheet_name=None)
# Load for values: wb = load_workbook('f.xlsx', data_only=True)
```

## Implementation anchors
### Pivot Table Construction
**CRITICAL: All pivot tables MUST use `cacheId=0`** to avoid `KeyError` in openpyxl.

```python
# 1. Cache Definition
cache = CacheDefinition(
    cacheSource=CacheSource(worksheetSource=WorksheetSource(ref="A1:D100", sheet="Source")),
    cacheFields=[CacheField(name="Cat", sharedItems=SharedItems(count=10)), ...]
)

# 2. Table Definition
pivot = TableDefinition(
    name="Pivot1", cacheId=0, 
    location=Location(ref="A3:B10", firstHeaderRow=1, firstDataRow=1, firstDataCol=1)
)

# 3. Field Configuration (Index-based)
pivot.pivotFields.append(PivotField(axis="axisRow")) # Field 0
pivot.pivotFields.append(PivotField(dataField=True))  # Field 3

# 4. Assignment
pivot.rowFields.append(RowColField(x=0))
pivot.dataFields.append(DataField(name="Sum", fld=3, subtotal="sum"))
pivot.cache = cache
ws_pivot._pivots.append(pivot)
```

## Workflow
1. **Data Prep**: Use `pandas` for analysis or `ws.append()` for raw data.
2. **Formatting**: Apply `Font`, `PatternFill`, or `Alignment` to cells.
3. **Pivot Setup**: Define `CacheSource` pointing to data range.
4. **Pivot Layout**: Map `pivotFields` to `rowFields`, `colFields`, or `dataFields`.
5. **Finalize**: Append pivot to worksheet `_pivots` and `save()`.

## Validation checks
- `cacheId == 0`: Mandatory for openpyxl compatibility.
- `fld` index: Must match the 0-based order of `cacheFields`.
- `Location.ref`: Ensure it does not overlap with existing data.
- `subtotal`: Valid values: `sum`, `count`, `average`, `max`, `min`, `product`, `stdDev`, `var`.

## Pitfalls
- **Non-zero cacheId**: Causes `KeyError` when re-opening files.
- **Calculation**: Pivot values only populate when the file is opened in Excel/LibreOffice.
- **Field Mismatch**: `cacheFields` order must strictly match source data column order.
- **Categorical Data**: Set `SharedItems(count=N)` for categorical fields in the cache.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
from openpyxl import Workbook
from openpyxl.pivot.table import TableDefinition, Location, PivotField, DataField, RowColField
from openpyxl.pivot.cache import CacheDefinition, CacheField, CacheSource, WorksheetSource, SharedItems

# 1. Create workbook with source data
wb = Workbook()
data_ws = wb.active
data_ws.title = "SourceData"

# Write your data (with headers in row 1)
data = [
    ["CategoryName", "ProductName", "Quantity", "Revenue"],
    ["Beverages", "Chai", 25, 450.00],
    ["Seafood", "Ikura", 12, 372.00],
    # ... more rows
]
for row in data:
    data_ws.append(row)

num_rows = len(data)

# 2. Create pivot table sheet
pivot_ws = wb.create_sheet("PivotAnalysis")

# 3. Define the cache (source data reference)
cache = CacheDefinition(
    cacheSource=CacheSource(
        type="worksheet",
        worksheetSource=WorksheetSource(
            ref=f"A1:D{num_rows}",  # Adjust to your data range
            sheet="SourceData"
        )
    ),
    cacheFields=[
        CacheField(name="CategoryName", sharedItems=SharedItems(count=8)),
        CacheField(name="ProductName", sharedItems=SharedItems(count=40)),
        CacheField(name="Quantity", sharedItems=SharedItems()),
        CacheField(name="Revenue", sharedItems=SharedItems()),
    ]
)

# 4. Create pivot table definition
pivot = TableDefinition(
    name="RevenueByCategory",
    cacheId=0,  # MUST be 0 for ALL pivot tables - any other value breaks openpyxl
    dataCaption="Values",
    location=Location(
        ref="A3:B10",  # Where pivot table will appear
        firstHeaderRow=1,
        firstDataRow=1,
        firstDataCol=1
    ),
)

# 5. Configure pivot fields (one for each source column)
# Fields are indexed 0, 1, 2, 3 matching cache field order

# Field 0: CategoryName - use as ROW
pivot.pivotFields.append(PivotField(axis="axisRow", showAll=False))
# Field 1: ProductName - not used (just include it)
pivot.pivotFields.append(PivotField(showAll=False))
# Field 2: Quantity - not used
pivot.pivotFields.append(PivotField(showAll=False))
# Field 3: Revenue - use as DATA (for aggregation)
pivot.pivotFields.append(PivotField(dataField=True, showAll=False))

# 6. Add row field reference (index of the field to use as rows)
pivot.rowFields.append(RowColField(x=0))  # CategoryName is field 0

# 7. Add data field with aggregation
pivot.dataFields.append(DataField(
    name="Total Revenue",
    fld=3,  # Revenue is field index 3
    subtotal="sum"  # Options: sum, count, average, max, min, product, stdDev, var
))

# 8. Attach cache and add to worksheet
pivot.cache = cache
pivot_ws._pivots.append(pivot)

wb.save('output_with_pivot.xlsx')
```
### Anchor 2
```python
from openpyxl import load_workbook

wb = load_workbook('file.xlsx')
ws = wb.active
value = ws['A1'].value

# Read calculated values (not formulas)
wb = load_workbook('file.xlsx', data_only=True)
```
