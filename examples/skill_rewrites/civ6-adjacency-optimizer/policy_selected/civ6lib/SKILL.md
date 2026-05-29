---
name: civ6lib
description: Civilization 6 district mechanics library. Use when working with district placement validation, adjacency bonus calculations, or understanding Civ6 game rules.
---

# Understanding Civ6 District Mechanics

## Capability and use cases
Reference for Civilization 6 (Gathering Storm) district placement validation and adjacency bonus calculations on hex grids.

## Required artifacts
- `placement_rules.py`: Validation logic.
- `adjacency_rules.py`: Adjacency calculation engine.
- `src.hex_utils`: Hex grid spatial utilities (neighbors, distance).

## API/tool patterns
```python
from civ6lib import (
    DistrictType, Tile, get_placement_rules, 
    get_adjacency_calculator
)

# Validate placement
rules = get_placement_rules(tiles, city_center=(21, 13), population=7)
result = rules.validate_placement(DistrictType.CAMPUS, 21, 14, {})

# Calculate adjacency
calc = get_adjacency_calculator(tiles)
total, per_district = calc.calculate_total_adjacency(placements)
```

## Implementation anchors
- **City Distance**: Min 4 tiles (same landmass); Min 3 tiles (different landmass).
- **District Distance**: Within 3 tiles of City Center.
- **Population Limit**: `max_specialty_districts = 1 + floor((population - 1) / 3)`.
- **Minor Bonus Rule**: Each +0.5 type is floored SEPARATELY, then summed. `floor(count/2)` per source type.
- **Destruction**: Placing districts destroys Woods, Rainforest, Marsh, and Bonus Resources.

## Workflow
1. **Terrain Check**: Ensure tile is not Mountain, Natural Wonder, Strategic Resource, or Luxury Resource.
2. **Slot Check**: Verify population allows a specialty district (Aqueduct, Dam, Canal, Neighborhood, Spaceport are exempt).
3. **Uniqueness Check**: Ensure specialty district is not already present in city (except Neighborhood).
4. **Specific Requirements**:
   - **Harbor/Water Park**: Coast/Lake adjacent to land.
   - **Encampment/Preserve**: NOT adjacent to City Center.
   - **Aqueduct**: Adjacent to City Center AND fresh water (Mountain, River, Lake, Oasis).
   - **Dam**: On Floodplains; river must cross 2+ tile edges.
   - **Aerodrome/Spaceport**: Flat land only.

## Validation checks
- Is tile within 3 hexes of City Center?
- Is the tile unoccupied by other districts/wonders?
- Are Strategic/Luxury resources absent?
- For Industrial Zones: Are adjacent Aqueducts/Dams/Canals present (+2)?
- For Commercial Hubs: Is the tile on a River (+2) or adjacent to a Harbor (+2)?

## Pitfalls
- **Adjacency Flooring**: Do not sum all 0.5 bonuses before flooring. `1 Mine (+0.5) + 1 District (+0.5) = 0`, not 1.
- **Resource Preservation**: Settling a City Center on Luxury/Strategic resources preserves them; placing a District does not (and is prohibited).
- **Feature Removal**: Placing a district may remove Woods/Rainforest, potentially lowering adjacency for existing Holy Sites/Campuses.

## Implementation Anchors
Use these source-derived patterns when the task requires the same API or workflow.
### Anchor 1
```python
from civ6lib import (
    # Placement
    DistrictType, Tile, PlacementRules, get_placement_rules,
    validate_district_count, validate_district_uniqueness,
    # Adjacency
    AdjacencyCalculator, get_adjacency_calculator,
)

# Validate a placement
rules = get_placement_rules(tiles, city_center=(21, 13), population=7)
result = rules.validate_placement(DistrictType.CAMPUS, 21, 14, {})
if result.valid:
    print("Valid placement!")

# Calculate adjacency bonus
calculator = get_adjacency_calculator(tiles)
total, per_district = calculator.calculate_total_adjacency(placements)
```
