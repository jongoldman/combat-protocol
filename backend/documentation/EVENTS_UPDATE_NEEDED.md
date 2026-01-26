# events.py Update Required

The `StateUpdateEvent` class needs to add position fields:

```python
@dataclass
class StateUpdateEvent(FightEvent):
    """Periodic state update with health, stamina, and damage"""
    fighter_a_health: float
    fighter_b_health: float
    fighter_a_stamina: float
    fighter_b_stamina: float
    fighter_a_head_damage: float
    fighter_a_body_damage: float
    fighter_a_leg_damage: float
    fighter_b_head_damage: float
    fighter_b_body_damage: float
    fighter_b_leg_damage: float
    
    # NEW FIELDS FOR v0.2.6 COLLISION DETECTION:
    fighter_a_pos_x: float = 0.0
    fighter_a_pos_z: float = 0.0
    fighter_b_pos_x: float = 0.0
    fighter_b_pos_z: float = 0.0
```

Jon, you'll need to add these 4 fields to your `StateUpdateEvent` class in `events.py`.
