# Combat Protocol v0.2.9 - Fist-Bump Feature Implementation Guide

## Overview
This document explains the changes needed to add the fist-bump intro sequence to Combat Protocol.

## Files to Modify
1. `simulator_v2.py` - Add fist-bump sequence logic
2. `app.py` - Update version number and add timing for fist-bump
3. `index.html` - Add sound effect support and fist-bump animation trigger
4. `static/sounds/fist_bump.mp3` - Add sound file (you'll need to source this)

## Changes Required

### 1. simulator_v2.py Changes

#### Update VERSION constant (line 8):
```python
VERSION: v0.2.9 - Fist-bump intro sequence

Major Changes from v0.2.8:
- Added pre-fight fist-bump sequence
- Fighters walk from corners, fist-bump, then back to combat distance  
- Smooth position interpolation during intro
```

#### In `__init__` method (around line 228-237), UPDATE positions:
```python
# OLD CODE:
self.fighter_a_pos = {'x': -2.0, 'z': 0.0}  # Left side (red corner)
self.fighter_b_pos = {'x': 2.0, 'z': 0.0}   # Right side (blue corner)

# NEW CODE:
# Starting positions for fist-bump sequence (corners)
self.corner_a_pos = {'x': -4.0, 'z': 0.0}  # Red corner (farther left)
self.corner_b_pos = {'x': 4.0, 'z': 0.0}   # Blue corner (farther right)

# Combat positions (after fist-bump)
self.combat_a_pos = {'x': -2.0, 'z': 0.0}
self.combat_b_pos = {'x': 2.0, 'z': 0.0}

# Fighter positions (start in corners)
self.fighter_a_pos = self.corner_a_pos.copy()
self.fighter_b_pos = self.corner_b_pos.copy()
```

#### ADD these helper methods after `_resolve_collision` method:
```python
def _lerp(self, start: float, end: float, t: float) -> float:
    """Linear interpolation between start and end"""
    return start + (end - start) * t

def _ease_in_out(self, t: float) -> float:
    """Smooth easing function (sine-based)"""
    return (1 - math.cos(t * math.pi)) / 2

def _generate_fist_bump_sequence(self) -> Generator[StateUpdateEvent, None, None]:
    """
    Generate the fist-bump intro sequence.
    
    Sequence:
    1. Fighters start in corners
    2. Walk toward center
    3. Pause at fist-bump distance (EXTENDED for story focus)
    4. Back to combat positions
    
    Yields StateUpdateEvent objects for position updates
    """
    # Phase 1: Walk from corners to center (1.2 seconds, 12 steps)
    steps_to_center = 12
    bump_distance = 1.0  # Distance apart during fist-bump
    
    for step in range(steps_to_center + 1):
        t = step / steps_to_center
        eased_t = self._ease_in_out(t)
        
        # Move toward center
        self.fighter_a_pos['x'] = self._lerp(self.corner_a_pos['x'], -bump_distance/2, eased_t)
        self.fighter_b_pos['x'] = self._lerp(self.corner_b_pos['x'], bump_distance/2, eased_t)
        
        yield StateUpdateEvent(
            event_type=EventType.STATE_UPDATE,
            timestamp=0,
            round_num=0,
            fighter_a_health=self.fighter_a_health,
            fighter_b_health=self.fighter_b_health,
            fighter_a_stamina=self.fighter_a_stamina,
            fighter_b_stamina=self.fighter_b_stamina,
            fighter_a_pos_x=self.fighter_a_pos['x'],
            fighter_a_pos_z=self.fighter_a_pos['z'],
            fighter_b_pos_x=self.fighter_b_pos['x'],
            fighter_b_pos_z=self.fighter_b_pos['z'],
            fighter_a_head_damage=self.fighter_a_head_damage,
            fighter_a_body_damage=self.fighter_a_body_damage,
            fighter_a_leg_damage=self.fighter_a_leg_damage,
            fighter_b_head_damage=self.fighter_b_head_damage,
            fighter_b_body_damage=self.fighter_b_body_damage,
            fighter_b_leg_damage=self.fighter_b_leg_damage,
        )
    
    # Phase 2: Pause at fist-bump position (EXTENDED - 8 frames = 0.8 seconds)
    # This creates the "story focus" on the fist-bump moment
    for _ in range(8):
        yield StateUpdateEvent(
            event_type=EventType.STATE_UPDATE,
            timestamp=0,
            round_num=0,
            fighter_a_health=self.fighter_a_health,
            fighter_b_health=self.fighter_b_health,
            fighter_a_stamina=self.fighter_a_stamina,
            fighter_b_stamina=self.fighter_b_stamina,
            fighter_a_pos_x=self.fighter_a_pos['x'],
            fighter_a_pos_z=self.fighter_a_pos['z'],
            fighter_b_pos_x=self.fighter_b_pos['x'],
            fighter_b_pos_z=self.fighter_b_pos['z'],
            fighter_a_head_damage=self.fighter_a_head_damage,
            fighter_a_body_damage=self.fighter_a_body_damage,
            fighter_a_leg_damage=self.fighter_a_leg_damage,
            fighter_b_head_damage=self.fighter_b_head_damage,
            fighter_b_body_damage=self.fighter_b_body_damage,
            fighter_b_leg_damage=self.fighter_b_leg_damage,
        )
    
    # Phase 3: Back to combat positions (0.8 seconds, 8 steps)
    steps_to_combat = 8
    
    for step in range(steps_to_combat + 1):
        t = step / steps_to_combat
        eased_t = self._ease_in_out(t)
        
        # Move to combat positions
        self.fighter_a_pos['x'] = self._lerp(-bump_distance/2, self.combat_a_pos['x'], eased_t)
        self.fighter_b_pos['x'] = self._lerp(bump_distance/2, self.combat_b_pos['x'], eased_t)
        
        yield StateUpdateEvent(
            event_type=EventType.STATE_UPDATE,
            timestamp=0,
            round_num=0,
            fighter_a_health=self.fighter_a_health,
            fighter_b_health=self.fighter_b_health,
            fighter_a_stamina=self.fighter_a_stamina,
            fighter_b_stamina=self.fighter_b_stamina,
            fighter_a_pos_x=self.fighter_a_pos['x'],
            fighter_a_pos_z=self.fighter_a_pos['z'],
            fighter_b_pos_x=self.fighter_b_pos['x'],
            fighter_b_pos_z=self.fighter_b_pos['z'],
            fighter_a_head_damage=self.fighter_a_head_damage,
            fighter_a_body_damage=self.fighter_a_body_damage,
            fighter_a_leg_damage=self.fighter_a_leg_damage,
            fighter_b_head_damage=self.fighter_b_head_damage,
            fighter_b_body_damage=self.fighter_b_body_damage,
            fighter_b_leg_damage=self.fighter_b_leg_damage,
        )
```

#### In `simulate_round_streaming` method, ADD position reset:
```python
def simulate_round_streaming(self, round_num: int) -> Generator[FightEvent, None, RoundResult]:
    """
    Generator that yields events for a single round.
    Returns RoundResult when round is complete.
    """
    self.current_round = round_num
    self.current_time = 0.0
    
    # ADD THIS: Reset positions to combat stance at start of each round
    self.fighter_a_pos = self.combat_a_pos.copy()
    self.fighter_b_pos = self.combat_b_pos.copy()
    
    # ... rest of method remains the same
```

#### In `simulate_match_streaming` method, ADD fist-bump sequence (around line 900):
```python
def simulate_match_streaming(self) -> Generator[FightEvent, None, MatchResult]:
    """
    Generator that yields all events for a complete match.
    Returns MatchResult when complete.
    """
    rounds = []
    
    # Match start
    yield MatchStartEvent(
        event_type=EventType.MATCH_START,
        timestamp=0,
        round_num=0,
        fighter_a_name=self.fighter_a.name,
        fighter_b_name=self.fighter_b.name,
    )
    
    # NEW: Fist-bump sequence before first round
    fist_bump_gen = self._generate_fist_bump_sequence()
    for event in fist_bump_gen:
        yield event
    
    # Continue with rest of match...
    for round_num in range(1, 6):
        # ... rest remains the same
```

---

### 2. app.py Changes

#### Update VERSION (line 34):
```python
APP_VERSION = "v0.2.9"  # Fist-bump intro sequence
```

#### Update banner (line 44):
```python
║                    VERSION: {APP_VERSION}                      ║
║               (FIST-BUMP INTRO SEQUENCE)                       ║
```

#### In `simulate_fight` function, the state_update handling already works!
No changes needed - the existing code handles StateUpdateEvent perfectly.

---

### 3. index.html Changes

#### ADD Sound Support (add this after the importmap, around line 840):
```javascript
// =====================================================
// SOUND EFFECTS
// =====================================================
const sounds = {
    fistBump: new Audio('/static/sounds/fist_bump.mp3')
};

// Preload sounds
for (let key in sounds) {
    sounds[key].load();
}

function playSound(soundName) {
    if (sounds[soundName]) {
        sounds[soundName].currentTime = 0;  // Reset to start
        sounds[soundName].play().catch(err => {
            console.log('Sound play failed (user interaction required):', err);
        });
    }
}
```

#### ADD Fist-bump Detection in state_update handler (around line 1145):
```javascript
eventSource.addEventListener('state_update', (e) => {
    const data = JSON.parse(e.data);
    
    console.log('📍 STATE_UPDATE received:', {
        modelA: !!modelA,
        modelB: !!modelB,
        pos_a_x: data.fighter_a_pos_x,
        pos_b_x: data.fighter_b_pos_x,
        round: data.round_num
    });
    
    // NEW: Detect fist-bump moment (round 0, fighters close together)
    if (data.round_num === 0 && modelA && modelB) {
        const distance = Math.abs(data.fighter_a_pos_x - data.fighter_b_pos_x);
        
        // If fighters are ~1.0m apart (fist-bump distance)
        if (distance < 1.2 && distance > 0.8) {
            // Check if this is first time at bump distance
            if (!window.fistBumpSoundPlayed) {
                playSound('fistBump');
                window.fistBumpSoundPlayed = true;
                
                // Optional: Add visual effect
                console.log('🤜🤛 FIST BUMP!');
            }
        }
    }
    
    // Update fighter positions if they exist in the data
    if (data.fighter_a_pos_x !== undefined && modelA) {
        modelA.position.x = data.fighter_a_pos_x;
        modelA.position.z = data.fighter_a_pos_z;
        console.log('✅ Updated modelA position');
    }
    
    // ... rest of state_update handling remains the same
});
```

#### RESET fist-bump flag on fight start (in startFight function, around line 1128):
```javascript
async function startFight() {
    const fighterA = fighterASelect.value;
    const fighterB = fighterBSelect.value;
    
    if (!fighterA || !fighterB || fighterA === fighterB) return;
    
    // NEW: Reset fist-bump flag
    window.fistBumpSoundPlayed = false;
    
    // ... rest of startFight remains the same
```

---

### 4. Sound File

You need to add a sound file at: `static/sounds/fist_bump.mp3`

**Where to get the sound:**
- **Freesound.org** (search "fist bump", "glove hit", or "boxing")
- **Mixkit.co** (free sound effects)
- **Record your own** (literally bump your fists together)
- **AI generate** (ElevenLabs sound effects)

**Sound characteristics:**
- Short (0.2-0.5 seconds)
- Punchy, satisfying "thump" or "thwack"
- Not too loud or harsh
- Format: MP3, 44.1kHz, mono or stereo

---

## Implementation Steps

1. **Backup your current files**
2. **Apply simulator_v2.py changes** (update version, add methods, modify match flow)
3. **Apply app.py changes** (update version number)
4. **Apply index.html changes** (add sound support, fist-bump detection)
5. **Create static/sounds/ directory** if it doesn't exist
6. **Add fist_bump.mp3 file**
7. **Test!**

## Testing Checklist

- [ ] Fighters start in corners (farther apart than usual)
- [ ] Fighters walk toward center smoothly
- [ ] Fighters pause at center (~1.0m apart)
- [ ] Sound plays during pause
- [ ] Fighters back up to combat positions
- [ ] Round 1 starts normally after sequence
- [ ] Total sequence takes ~2.8 seconds
- [ ] Sound only plays once per fight
- [ ] Works on both local and production

## Timing Breakdown

- **Phase 1 (Walk to center):** 12 frames × 0.1s = 1.2 seconds
- **Phase 2 (Fist-bump pause):** 8 frames × 0.1s = 0.8 seconds ⭐ **Story focus**
- **Phase 3 (Back to combat):** 8 frames × 0.1s = 0.8 seconds
- **Total:** ~2.8 seconds

The extended pause in Phase 2 creates the "story beat" you requested - the action slows down to emphasize the sportsmanship moment.

## Notes

- Sound requires user interaction to play in most browsers (autoplay policy)
- The sound will play when fighters reach fist-bump position
- If sound doesn't play, it's likely due to browser autoplay restrictions
- The sequence runs before Round 1, identified by `round_num === 0`

## Version

Combat Protocol v0.2.9 - Fist-Bump Intro Sequence
