---
name: map-optimization-strategy
description: Strategy for solving constraint optimization problems on spatial maps. Use when you need to place items on a grid/map to maximize some objective while satisfying constraints.
---

# Map-Based Constraint Optimization Strategy

## Capability and use cases
Systematic placement optimization on spatial grids to maximize objectives while respecting hard constraints. Prevents combinatorial explosion (O(M^N)) where exhaustive search fails (e.g., 50 tiles, 5 items = 312M combinations).

## Required artifacts
- `map_tiles`: Grid or spatial data structure.
- `constraints`: Hard rules (terrain, range, blockages).
- `num_placements`: Target count of items to place.

## API/tool patterns
```python
def optimize_placements(map_tiles, constraints, num_placements):
    # Phase 1: Prune
    candidates = [t for t in map_tiles if is_valid_tile(t, constraints)]

    # Phase 2: Score and rank
    scored = [(tile, score_tile(tile, candidates)) for tile in candidates]
    scored.sort(key=lambda x: -x[1])
    high_value = scored[:top_k]

    # Phase 3: Anchor search
    best_solution = None
    for anchor in get_anchor_candidates(high_value, constraints):
        solution = greedy_expand(anchor, candidates, num_placements, constraints)
        solution = local_search(solution, candidates, constraints)
        if solution.score > best_score: 
            best_solution = solution
    return best_solution
```

## Implementation anchors
- **Pruning Logic**: Remove tiles that are Invalid (violate hard constraints), Dominated (strictly better tile exists), or Isolated (too far for clusters).
- **Scoring Metrics**: Intrinsic value + Adjacency potential + Cluster potential.
- **Anchor Search**: Use high-value spots as fixed points to constrain the search space.

## Workflow
1. **Prune Search Space**: Target 70-90% reduction by eliminating non-contributing tiles.
2. **Identify High-Value Spots**: Rank remaining tiles by scoring potential.
3. **Anchor Point Search**: 
    - Select anchor candidates from top-ranked tiles.
    - Expand greedily to maximize marginal value.
    - Apply local search (swapping/moving) to refine the solution.

## Validation checks
- **is_valid_tile**: Verify terrain, range, and blockage constraints per tile.
- **Constraint Propagation**: Update validity of remaining tiles immediately after each placement.
- **Final Verification**: Ensure the complete solution satisfies ALL global and local constraints.

## Pitfalls
- **Ignoring Interactions**: Placing item A may change the value or validity of item B (adjacency effects).
- **Over-optimizing Metrics**: Balancing intrinsic value with flexibility for future placements.
- **Validation Omission**: Failing to verify the final aggregate solution against hard constraints.