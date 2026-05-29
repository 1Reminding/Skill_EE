---
name: fuzzy-match
description: A toolkit for fuzzy string matching and data reconciliation for entity names (companies, people) across datasets with spelling variations or typos.
license: MIT
---

# Fuzzy Matching

## Capability and use cases
Reconcile disparate datasets by calculating string similarity. Primary use cases include entity resolution, deduplication, and joining tables on non-identical string keys.

## Required artifacts
- `difflib` (Python Standard Library)
- `rapidfuzz` (Optional, recommended for performance/scale)
- `re` (Regex for normalization)

## API/tool patterns

### difflib (Standard)
```python
from difflib import SequenceMatcher, get_close_matches

# Similarity ratio (0 to 1)
ratio = SequenceMatcher(None, "Apple Inc.", "Apple Incorporated").ratio()

# Best match from list
matches = get_close_matches("appel", ["apple", "peach"], n=1, cutoff=0.6)
```

### rapidfuzz (High Performance)
```python
from rapidfuzz import fuzz, process

# Metrics
ratio = fuzz.ratio("test", "test!")
partial = fuzz.partial_ratio("test", "this is a test!")

# Extraction
best = process.extractOne("new york jets", ["Atlanta Falcons", "New York Jets"])
```

## Implementation anchors

### Normalization Function
```python
import re
def normalize(text):
    text = text.lower()
    text = re.sub(r'[^\w\s]', '', text)
    text = " ".join(text.split())
    return text.replace("limited", "ltd").replace("corporation", "corp")
```

## Workflow
1. **Normalize**: Apply `normalize()` to both source and target strings.
2. **Containment Check**: Perform a simple `if dirty.lower() in clean.lower()` check for speed.
3. **Fuzzy Fallback**: If no match, use `get_close_matches` or `process.extractOne` with a defined cutoff.

## Validation checks
- **Thresholds**: Use a default `cutoff=0.6` for `difflib` or `score_cutoff=60` for `rapidfuzz`.
- **Manual Review**: Sample matches with scores between 0.6 and 0.8 for false positives.

## Pitfalls
- **Performance**: `difflib` is O(N*M) and slow for large datasets; use `rapidfuzz` for O(N) performance.
- **False Positives**: Short strings (e.g., "IBM" vs "I") often yield high similarity ratios without being matches.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
import re

def normalize(text):
    # Convert to lowercase
    text = text.lower()
    # Remove special characters
    text = re.sub(r'[^\w\s]', '', text)
    # Normalize whitespace
    text = " ".join(text.split())
    # Common abbreviations
    text = text.replace("limited", "ltd").replace("corporation", "corp")
    return text

s1 = "Acme  Corporation, Inc."
s2 = "acme corp inc"
print(normalize(s1) == normalize(s2))
```
### Anchor 2
```python
from rapidfuzz import fuzz, process

# Simple Ratio
score = fuzz.ratio("this is a test", "this is a test!")
print(score)

# Partial Ratio (good for substrings)
score = fuzz.partial_ratio("this is a test", "this is a test!")
print(score)

# Extraction
choices = ["Atlanta Falcons", "New York Jets", "New York Giants", "Dallas Cowboys"]
best_match = process.extractOne("new york jets", choices)
print(best_match)
# Output: ('New York Jets', 100.0, 1)
```
