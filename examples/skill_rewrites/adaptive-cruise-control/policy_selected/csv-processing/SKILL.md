---
name: csv-processing
description: Use this skill when reading sensor data from CSV files, writing simulation results to CSV, processing time-series data with pandas, or handling missing values in datasets.
---

# CSV Processing with Pandas

## Capability and use cases
- Ingesting sensor data and time-series datasets.
- Persisting simulation results or computed metrics.
- Cleaning datasets with missing or null values.

## Required artifacts
- `pandas` library.
- Input/Output `.csv` files.

## API/tool patterns
```python
import pandas as pd

# Standard read/write
df = pd.read_csv('data.csv', na_values=['', 'NA', 'null'])
df.to_csv('output.csv', index=False)

# Construction from records
results = [{'time': 0.1, 'val': 1.0}, {'time': 0.2, 'val': 2.0}]
df = pd.DataFrame(results)
```

## Implementation anchors
- **Filtering**: `df[(df['time'] >= 30) & (df['time'] < 60)]` or `df[df['col'].notna()]`.
- **Iteration**: `for index, row in df.iterrows(): process(row['col1'])`.
- **Computation**: `df['diff'] = df['col1'] - df['col2']`.
- **Statistics**: `df['col'].mean()`, `df['col'].std()`, `df['col'].max()`, `df['col'].min()`.

## Workflow
1. **Load**: Use `pd.read_csv` with `na_values` to normalize nulls.
2. **Inspect**: Check structure with `df.head()` and `df.columns.tolist()`.
3. **Clean**: Identify gaps using `df.isnull().sum()`.
4. **Process**: Apply filters, compute new columns, or iterate via `iterrows()`.
5. **Export**: Save results using `to_csv(index=False)`.

## Validation checks
- `df.isnull().sum()` to count missing entries per column.
- `pd.isna(row['column'])` for scalar null checks during iteration.
- `len(df)` to verify record counts.

## Pitfalls
- **Index Persistence**: `to_csv()` includes the index by default; use `index=False` to avoid extra columns.
- **Boolean Logic**: Use `&` and `|` with parentheses for filtering; standard `and`/`or` will fail on Series objects.