# Combat Protocol - Known Issues

## Version: v0.2.9

This document tracks known issues and their root causes for future resolution.

---

## 🔴 HIGH PRIORITY

### Collision Detection - Visual Ghosting During Combat

**Status:** Known Issue - Deferred to Advanced Modeling Phase  
**Affects:** v0.2.8, v0.2.9  
**Date Identified:** January 19, 2026

#### Description
Fighters visually overlap ("ghost through each other") during combat, particularly when animations show extended punches or kicks. This occurs despite the collision detection system reporting correct separation distances.

#### Observed Behavior
- Fighters appear to overlap in the 3D visualization
- Console logs show correct positions and distances (e.g., 3.2 meters apart)
- Ghosting happens intermittently throughout the fight
- When animations are paused, fighters may drift slightly before settling
- Most noticeable during active striking exchanges

#### Root Cause Analysis

**The Issue:** Architectural mismatch between animation system and collision detection.

1. **Collision Detection System (Backend)**
   - Tracks fighter positions as points with capsule collision volumes
   - Works at the center-of-mass level
   - `min_separation` parameter controls minimum distance between centers
   - Current setting: `self.min_separation = 0.4` (meters)
   - **Status: Working correctly** - Console logs confirm accurate distance tracking

2. **3D Models and Animations (Frontend)**
   - GLB files contain baked animations (punching, kicking, etc.)
   - Animations extend limbs far beyond the fighter's center position
   - Example: Punch animation may extend arm 1.5 meters forward
   - These extensions are **not tracked by collision detection**
   - Animations operate in their own coordinate space

3. **The Conflict**
   - Backend: "Fighters are 3.2 meters apart" ✅
   - Frontend: "Arm extends 1.5m forward + leg extends 1.5m forward = overlap" ❌
   - Result: Visually appear to overlap despite correct positional separation

#### Why Simple Fixes Don't Work

**Attempted Solutions:**
- ✗ Increasing `min_separation` to 2.0+ meters: Fighters look unnaturally far apart
- ✗ Model centering offsets: Already implemented correctly
- ✗ Position update synchronization: Already working properly

**The Core Problem:**
The collision system would need to know:
- Which animation frame is playing
- Where each limb is at that moment
- The actual 3D geometry of extended limbs
- Real-time collision between animated meshes

This requires a fundamentally different architecture.

#### Proper Solution (Future Work)

**Prerequisites:**
1. **Advanced Blender Modeling** (In Progress)
   - Custom fighter models with full control over geometry
   - Skeletal rig for programmatic animation control
   - Defined collision volumes per body part

2. **Animation-Aware Collision System**
   ```
   Option A: Capsule-per-limb with animation tracking
   - Head capsule: fixed to head bone
   - Torso capsule: fixed to spine bone
   - Arm capsules: fixed to upper_arm/lower_arm bones
   - Leg capsules: fixed to upper_leg/lower_leg bones
   - Update capsule positions every frame based on bone transforms
   
   Option B: Custom animation system
   - Design animations that respect collision boundaries
   - Procedural animation based on game state
   - IK (Inverse Kinematics) to adjust strikes based on distance
   
   Option C: Hybrid approach
   - Collision detection prevents center-of-mass overlap
   - Animations adjust/blend based on proximity
   - "Close range" vs "long range" animation variants
   ```

3. **Three.js Integration**
   - Access to bone transforms in real-time
   - Update collision capsules based on skeletal positions
   - Possibly use Three.js Raycasting for limb collision detection

#### Workaround for Current Version

**User Impact:** Low
- Collision detection prevents gameplay issues (fighters can't stand on same spot)
- Visual overlap is cosmetic, doesn't affect fight outcomes
- Most noticeable to developers, less so to end users

**Temporary Measures:**
- Console logging confirms system integrity
- Debug visualization (distance line) helps monitor actual separation
- Fist-bump sequence demonstrates position control works correctly

#### Action Items

**Before Resuming Work on This Issue:**
- [ ] Complete advanced Blender modeling phase
- [ ] Implement skeletal animation system
- [ ] Research Three.js bone transform access
- [ ] Design animation system that's collision-aware
- [ ] Consider IK for dynamic punch/kick adjustment

**Reference Files:**
- `simulator_v2.py` - Backend collision detection (capsule system)
- `index.html` - Frontend 3D rendering and position updates
- `FighterCapsules` class (lines 35-155 in simulator_v2.py)
- Position update handler (lines ~1266-1312 in index.html)

**Related Features Working Correctly:**
- ✅ Capsule-based collision detection (backend)
- ✅ Position synchronization between backend and frontend
- ✅ Fist-bump intro sequence
- ✅ Distance calculations and logging
- ✅ Model centering and offset management

---

## 🟡 MEDIUM PRIORITY

### Fist-Bump Sequence - Minor Timing Issue

**Status:** Cosmetic - Low Priority  
**Affects:** v0.2.9

#### Description
During the fist-bump intro sequence (Round 0), fighters sometimes show brief overlap in the 3D view even though console shows correct separation.

#### Root Cause
Same as collision ghosting issue above - baked animations extend limbs during fist-bump approach.

#### Impact
Minimal - it's a brief pre-fight sequence, doesn't affect gameplay.

#### Future Fix
Will be resolved with the same animation-aware collision system described above.

---

## 📋 NOTES FOR FUTURE DEVELOPMENT

### Lessons Learned

1. **Animation and Physics Must Be Coupled**
   - Can't treat them as independent systems
   - Physics needs to know about animation state
   - Or animations need to respect physics constraints

2. **Model Design Matters**
   - Pre-baked animations limit collision accuracy
   - Need programmatic control over skeletal animation
   - Custom models designed for the physics system work best

3. **Debug Infrastructure Is Critical**
   - Console logging revealed the true separation distances
   - Visual debug line (green/yellow/red) helps identify issues
   - Without these, would have blamed wrong system

4. **Incremental Progress Works**
   - v0.2.6: Basic bounding box collision
   - v0.2.8: Capsule-based collision (big improvement)
   - v0.2.9: Fist-bump sequence (proves position control)
   - Next: Animation-aware collision (requires Blender work first)

### Technical Debt

**Low Priority (Can Live With):**
- Visual ghosting during combat
- Occasional popping when collision resolution triggers

**Medium Priority (Should Address Eventually):**
- Couple animation system with collision detection
- Add per-limb collision volumes that follow bones
- Implement animation blending based on distance

**High Priority (Blockers for Production):**
- None currently - system is functional

---

## 🔧 DEBUGGING TOOLS AVAILABLE

For investigating collision issues:

1. **Console Logging**
   - 🔴/🔵 Fighter position updates
   - 📏 Distance measurements
   - 🥊 Round start markers

2. **Visual Debug Line**
   - Green: Good separation (3+ meters)
   - Yellow: Close range (2-3 meters)
   - Red: Too close (< 2 meters)

3. **Browser DevTools**
   - F12 → Console tab
   - Watch for STATE_UPDATE events
   - Monitor distance_3d vs distance_sim

---

## 📝 VERSION HISTORY

**v0.2.9** (Current)
- Added fist-bump intro sequence
- Fixed position reset after fist-bump
- Added enhanced debug logging
- Documented collision/animation issue

**v0.2.8**
- Implemented capsule-based collision detection
- Replaced simple bounding box system
- Added per-body-part collision volumes

**v0.2.6**
- Initial collision detection (bounding box)
- Basic position tracking and updates

---

**Last Updated:** January 19, 2026  
**Maintained By:** Development Team  
**Next Review:** After Blender modeling phase completion
