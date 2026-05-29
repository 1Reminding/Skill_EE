---
name: hex-grid-spatial
description: Hex grid spatial utilities for offset coordinate systems. Use when working with hexagonal grids, calculating distances, finding neighbors, or spatial queries on hex maps.
---

### Capability and use cases
Spatial operations for odd-r offset hexagonal grids (odd rows shifted right). Supports neighbor detection, distance calculation, and range queries for tile-based maps.

### Required artifacts
- Python 3.x environment
- Coordinate system: (0,0) bottom-left, X+ right, Y+ up

### API/tool patterns
```python
def get_neighbors(x, y):
    if y % 2 == 0: # even row
        ds = [(1,0), (0,-1), (-1,-1), (-1,0), (-1,1), (0,1)]
    else: # odd row
        ds = [(1,0), (1,-1), (0,-1), (-1,0), (0,1), (1,1)]
    return [(x + dx, y + dy) for dx, dy in ds]

def hex_distance(x1, y1, x2, y2):
    def to_cube(c, r):
        cx = c - (row - (row & 1)) // 2
        cz = r
        return cx, -cx - cz, cz
    c1, c2 = to_cube(x1, y1), to_cube(x2, y2)
    return sum(abs(a - b) for a, b in zip(c1, c2)) // 2

def get_tiles_in_range(x, y, radius):
    return [(nx, ny) for dx in range(-radius, radius + 1) 
            for dy in range(-radius, radius + 1)
            if (nx := x + dx, ny := y + dy) != (x, y) 
            and hex_distance(x, y, nx, ny) <= radius]
```

### Implementation anchors
- **Direction Indices**: 0=E, 1=NE, 2=NW, 3=W, 4=SW, 5=SE.
- **Cube Conversion**: `cx = col - (row - (row & 1)) // 2`, `cz = row`, `cy = -cx - cz`.
- **Parity Logic**: Odd rows (`y % 2 == 1`) are shifted right by 0.5 hex relative to even rows.

### Workflow
1. Determine row parity using `y % 2`.
2. Select neighbor offset set based on parity.
3. For distance/range, convert offset coordinates to cube coordinates to use the Manhattan-style hex distance formula.

### Validation checks
- Adjacency: `hex_distance(p1, p2) == 1` for all neighbors.
- Cube Invariant: `cx + cy + cz == 0` for all converted coordinates.
- Range: `get_tiles_in_range` must exclude the center tile `(x, y)`.

### Pitfalls
- **Parity Mismatch**: Applying even-row offsets to odd rows (causes 1-tile drift).
- **Coordinate Type**: Confusing odd-r (row-shifted) with odd-q (column-shifted) systems.
- **Distance Error**: Using standard Manhattan distance `abs(x1-x2) + abs(y1-y2)` instead of cube-based hex distance.