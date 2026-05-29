---
name: sqlite-map-parser
description: Parse SQLite databases into structured JSON data. Use when exploring unknown database schemas, understanding table relationships, and extracting map data as JSON.
---

# SQLite to Structured JSON

## Capability and use cases
- Schema discovery and relationship mapping for unknown SQLite databases.
- Extraction of spatial/grid data into structured JSON.
- Transformation of relational tables into hierarchical or keyed JSON objects.

## Required artifacts
- SQLite database file.
- Python `sqlite3` and `json` libraries.

## API/tool patterns
- **Schema Discovery**: `SELECT name FROM sqlite_master WHERE type='table';` 
- **Column Info**: `PRAGMA table_info(TableName);` (Check 'pk' column for primary keys).
- **Relationships**: `PRAGMA foreign_key_list(TableName);` 
- **Indexes**: `PRAGMA index_list(TableName);` and `PRAGMA index_info(index_name);` 

## Implementation anchors
```python
import sqlite3, json

def parse_sqlite_to_json(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Metadata extraction
    cursor.execute("SELECT * FROM MetadataTable LIMIT 1")
    meta = dict(cursor.fetchone())
    
    # Main data mapping
    data = {}
    cursor.execute("SELECT * FROM MainTable")
    for r in cursor.fetchall():
        # Grid math: x = r['ID'] % meta['width']; y = r['ID'] // meta['width']
        data[r['ID']] = dict(r)
        
    conn.close()
    return {"metadata": meta, "items": list(data.values())}

def safe_query(cursor, query):
    try:
        cursor.execute(query)
        return cursor.fetchall()
    except sqlite3.OperationalError: return []
```

## Workflow
1. **Explore**: Identify tables via `sqlite_master` and column types via `PRAGMA` commands.
2. **Map**: Identify Foreign Keys and ID-based join patterns (e.g., `MainTable.ID = RelatedTable.ID`).
3. **Extract**: Query metadata and primary tables; use `sqlite3.Row` for direct dictionary conversion.
4. **Transform**: Apply coordinate math (`id % width`) or join related data into the primary dictionary.
5. **Output**: Structure as Map (keyed by `"x,y"`) or Array of objects based on access requirements.

## Validation checks
- Row counts: `SELECT COUNT(*) FROM TableName;` 
- Uniqueness: `SELECT DISTINCT Col FROM TableName;` 
- Data integrity: `SELECT COUNT(*) FROM TableName WHERE Col IS NULL;` 

## Pitfalls
- **Missing Tables**: Always wrap queries in `try/except sqlite3.OperationalError` using a `safe_query` pattern.
- **Join Loss**: Use `LEFT JOIN` instead of `INNER JOIN` to prevent dropping records with missing relations.
- **Grid Alignment**: Ensure `width` used in `id % width` matches the actual database metadata to avoid coordinate shifts.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
import sqlite3
import json

def parse_sqlite_to_json(db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    cursor = conn.cursor()

    # 1. Explore schema
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # 2. Get dimensions/metadata from config table
    cursor.execute("SELECT * FROM MetadataTable LIMIT 1")
    metadata = dict(cursor.fetchone())

    # 3. Build indexed data structure
    data = {}
    cursor.execute("SELECT * FROM MainTable")
    for row in cursor.fetchall():
        key = row["ID"]  # or compute: (row["X"], row["Y"])
        data[key] = dict(row)

    # 4. Join related data
    cursor.execute("SELECT * FROM RelatedTable")
    for row in cursor.fetchall():
        key = row["ID"]
        if key in data:
            data[key]["extra_field"] = row["Value"]

    conn.close()
    return {"metadata": metadata, "items": list(data.values())}
```
