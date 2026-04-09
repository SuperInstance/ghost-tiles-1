"""Ghost Tiles — Invisible computational tiles that influence visible state.

Ghost tiles exist in the "logical" layer, affecting computations
without manifesting in the "physical" layer. Like dark matter
for tile-based systems.
"""

import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Tuple


class GhostPhase(Enum):
    TEMPORAL = "temporal"      # Exists for a duration then fades
    PERMANENT = "permanent"    # Persists until explicitly removed
    RECURRING = "recurring"    # Periodically strengthens then weakens


class FalloffType(Enum):
    INVERSE_LINEAR = "inverse-linear"
    INVERSE_SQUARE = "inverse-square"
    EXPONENTIAL = "exponential"
    CONSTANT = "constant"


@dataclass
class Position:
    x: float
    y: float
    
    def distance_to(self, other: "Position") -> float:
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)


@dataclass
class GhostTile:
    """An invisible tile that influences visible tiles within its radius."""
    position: Position
    tile_type: str = "influence"
    phase: GhostPhase = GhostPhase.TEMPORAL
    strength: float = 0.5
    radius: float = 5.0
    falloff: FalloffType = FalloffType.INVERSE_SQUARE
    effect_property: str = "confidence"
    effect_operation: str = "multiply"
    effect_factor: float = 1.2
    age: int = 0
    max_age: int = 100
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def effective_strength(self) -> float:
        """Calculate strength considering age and phase."""
        base = self.strength
        if self.phase == GhostPhase.TEMPORAL:
            decay = max(0, 1 - self.age / self.max_age)
            return base * decay
        elif self.phase == GhostPhase.RECURRING:
            cycle = math.sin(self.age * 0.1) * 0.3 + 0.7
            return base * cycle
        return base
    
    def influence_at(self, pos: Position) -> float:
        """Calculate influence strength at a given position."""
        dist = self.position.distance_to(pos)
        if dist > self.radius:
            return 0.0
        
        effective = self.effective_strength()
        if self.falloff == FalloffType.INVERSE_LINEAR:
            return effective * (1 - dist / self.radius)
        elif self.falloff == FalloffType.INVERSE_SQUARE:
            return effective / (1 + dist**2)
        elif self.falloff == FalloffType.EXPONENTIAL:
            return effective * math.exp(-3 * dist / self.radius)
        return effective  # CONSTANT
    
    def tick(self) -> bool:
        """Advance age. Returns False if ghost should be removed."""
        self.age += 1
        if self.phase == GhostPhase.TEMPORAL and self.age >= self.max_age:
            return False
        return True


class VisibleTile:
    """A regular visible tile that can be affected by ghosts."""
    position: Position
    properties: Dict[str, float] = field(default_factory=dict)
    
    def __init__(self, x: float, y: float, **properties):
        self.position = Position(x, y)
        self.properties = dict(properties)
    
    def apply_effect(self, operation: str, factor: float, prop: str = "value"):
        """Apply a ghost effect to a property."""
        current = self.properties.get(prop, 1.0)
        if operation == "multiply":
            self.properties[prop] = current * factor
        elif operation == "add":
            self.properties[prop] = current + factor
        elif operation == "set":
            self.properties[prop] = factor
        elif operation == "clamp_min":
            self.properties[prop] = max(current, factor)
        elif operation == "clamp_max":
            self.properties[prop] = min(current, factor)


class GhostField:
    """A field of ghost tiles that influence visible tiles."""
    
    def __init__(self):
        self._ghosts: List[GhostTile] = []
        self._visible: List[VisibleTile] = []
    
    def add_ghost(self, ghost: GhostTile) -> GhostTile:
        self._ghosts.append(ghost)
        return ghost
    
    def add_visible(self, tile: VisibleTile) -> VisibleTile:
        self._visible.append(tile)
        return tile
    
    def propagate(self) -> Dict[str, List[Tuple[float, float]]]:
        """Calculate all ghost influences on visible tiles.
        Returns {tile_index: [(influence_strength, ghost_index), ...]}
        """
        result = {}
        for i, visible in enumerate(self._visible):
            influences = []
            for j, ghost in enumerate(self._ghosts):
                inf = ghost.influence_at(visible.position)
                if inf > 0.001:  # Threshold
                    influences.append((inf, j))
            result[str(i)] = influences
        return result
    
    def apply_influences(self) -> Dict[str, float]:
        """Apply all ghost effects to visible tiles.
        Returns total influence applied per visible tile.
        """
        propagation = self.propagate()
        totals = {}
        
        for tile_idx, influences in propagation.items():
            total = 0.0
            visible = self._visible[int(tile_idx)]
            for strength, ghost_idx in influences:
                ghost = self._ghosts[ghost_idx]
                visible.apply_effect(
                    ghost.effect_operation,
                    ghost.effect_factor * strength,
                    ghost.effect_property
                )
                total += strength
            totals[tile_idx] = total
        
        return totals
    
    def tick(self) -> int:
        """Advance all ghosts. Remove expired ones. Returns count remaining."""
        self._ghosts = [g for g in self._ghosts if g.tick()]
        return len(self._ghosts)
    
    def ghost_count(self) -> int:
        return len(self._ghosts)
    
    def visible_count(self) -> int:
        return len(self._visible)
    
    def summary(self) -> dict:
        return {
            "ghosts": len(self._ghosts),
            "visible": len(self._visible),
            "types": list(set(g.tile_type for g in self._ghosts)),
        }


class GhostComputation:
    """Multi-phase computation using ghost tiles as intermediate state."""
    
    def __init__(self):
        self.field = GhostField()
        self._phases: List[Callable[[GhostField], GhostField]] = []
        self._current_phase = 0
    
    def add_phase(self, fn: Callable[[GhostField], GhostField]):
        """Add a computation phase. Each phase receives the field."""
        self._phases.append(fn)
        return self
    
    def run(self, initial_ghosts: List[GhostTile] = None) -> GhostField:
        """Run all phases sequentially."""
        if initial_ghosts:
            for g in initial_ghosts:
                self.field.add_ghost(g)
        
        for i, phase in enumerate(self._phases):
            self._current_phase = i
            self.field = phase(self.field)
            self.field.tick()
        
        return self.field
    
    def current_phase(self) -> int:
        return self._current_phase
