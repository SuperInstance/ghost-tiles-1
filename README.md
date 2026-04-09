# Ghost Tiles

Invisible computational tiles that influence visible state. Like dark matter for tile-based systems.

## Concept

Ghost tiles exist in the logical layer, affecting computations without manifesting in the physical layer.

## Phases

- **Temporal**: Exists for a duration then fades
- **Permanent**: Persists until explicitly removed
- **Recurring**: Periodically strengthens then weakens

## Usage

```python
from tiles import GhostTile, GhostField, VisibleTile, Position, FalloffType, GhostPhase

field = GhostField()
field.add_visible(VisibleTile(5, 5, confidence=0.9))
field.add_ghost(GhostTile(Position(6, 4), 'attractor', GhostPhase.PERMANENT,
    strength=0.8, radius=5.0, falloff=FalloffType.INVERSE_SQUARE,
    effect_property='confidence', effect_operation='multiply', effect_factor=1.3))

totals = field.apply_influences()
```

Part of the [Lucineer ecosystem](https://github.com/Lucineer/the-fleet).