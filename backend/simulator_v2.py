# simulator_v2.py
"""
Event-based Muay Thai simulator for Combat Protocol.

This version emits structured FightEvent objects instead of directly
controlling display. This allows any renderer to visualize the fight.

VERSION: v0.2.9 - Fist-bump feature with collision detection fix

Major Changes from v0.2.8:
- Added pre-fight fist-bump intro sequence
- Fixed collision detection regression (fighters now stay at combat distance)
- Capsule-based collision detection maintained during combat
- Each fighter has capsules for: torso, head, arms, legs
- More realistic hit detection and physical spacing
"""

import random
import time
import math
from dataclasses import dataclass
from typing import List, Tuple, Generator, Optional
from fighter import Fighter
from events import (
    FightEvent, FighterID, MoveType, TargetZone, StrikeResult, EventType,
    MatchStartEvent, RoundStartEvent, RoundEndEvent, MatchEndEvent,
    StrikeEvent, ClinchEvent, ClinchExitEvent, KnockdownEvent, RecoveryEvent,
    StateUpdateEvent, BreakStartEvent, CommentaryEvent, event_to_dict
)


# ============================================================================
# CAPSULE COLLISION SYSTEM (Level 2)
# ============================================================================

class FighterCapsules:
    """
    Represents a fighter's body as a collection of capsules.
    Each capsule is a line segment with radius (cylinder + hemispheres on ends).
    This provides much more realistic collision than simple bounding boxes.
    """
    def __init__(self, position: dict, height_cm: float):
        """
        Create capsule representation for a fighter.
        
        Args:
            position: Fighter's center position {'x': float, 'z': float}
            height_cm: Fighter's height in cm
        """
        self.position = position
        self.height_m = height_cm / 100.0
        
        # Capsule definitions (start point, end point, radius)
        # All in local coordinates relative to fighter position
        
        # Torso: vertical from hips to shoulders
        torso_bottom = self.height_m * 0.3  # Hip height
        torso_top = self.height_m * 0.85     # Shoulder height
        self.torso = {
            'start': (0, torso_bottom, 0),
            'end': (0, torso_top, 0),
            'radius': 0.25  # 25cm radius torso
        }
        
        # Head: small capsule at top
        self.head = {
            'start': (0, torso_top, 0),
            'end': (0, self.height_m, 0),
            'radius': 0.12  # 12cm radius head
        }
        
        # Left arm: from shoulder outward
        self.left_arm = {
            'start': (-0.25, torso_top - 0.05, 0),
            'end': (-0.65, torso_top - 0.45, 0.15),  # Extended forward slightly
            'radius': 0.08  # 8cm radius arm
        }
        
        # Right arm: from shoulder outward
        self.right_arm = {
            'start': (0.25, torso_top - 0.05, 0),
            'end': (0.65, torso_top - 0.45, 0.15),  # Extended forward slightly
            'radius': 0.08  # 8cm radius arm
        }
        
        # Left leg: from hip downward
        self.left_leg = {
            'start': (-0.15, torso_bottom, 0),
            'end': (-0.15, 0, 0),
            'radius': 0.10  # 10cm radius leg
        }
        
        # Right leg: from hip downward  
        self.right_leg = {
            'start': (0.15, torso_bottom, 0),
            'end': (0.15, 0, 0),
            'radius': 0.10  # 10cm radius leg
        }
        
    def get_world_capsule(self, capsule: dict) -> dict:
        """Convert capsule from local to world coordinates"""
        x_offset = self.position['x']
        z_offset = self.position['z']
        
        return {
            'start': (
                capsule['start'][0] + x_offset,
                capsule['start'][1],
                capsule['start'][2] + z_offset
            ),
            'end': (
                capsule['end'][0] + x_offset,
                capsule['end'][1],
                capsule['end'][2] + z_offset
            ),
            'radius': capsule['radius']
        }
    
    def get_all_capsules(self) -> list:
        """Get all capsules in world coordinates"""
        return [
            self.get_world_capsule(self.torso),
            self.get_world_capsule(self.head),
            self.get_world_capsule(self.left_arm),
            self.get_world_capsule(self.right_arm),
            self.get_world_capsule(self.left_leg),
            self.get_world_capsule(self.right_leg)
        ]


def capsule_distance(cap1: dict, cap2: dict) -> float:
    """
    Calculate minimum distance between two capsules.
    Returns negative value if penetrating.
    
    Simplified version using capsule midpoints - fast enough for real-time.
    """
    # Get midpoints of each capsule
    s1_start, s1_end = cap1['start'], cap1['end']
    s2_start, s2_end = cap2['start'], cap2['end']
    
    mid1 = (
        (s1_start[0] + s1_end[0]) / 2,
        (s1_start[1] + s1_end[1]) / 2,
        (s1_start[2] + s1_end[2]) / 2
    )
    mid2 = (
        (s2_start[0] + s2_end[0]) / 2,
        (s2_start[1] + s2_end[1]) / 2,
        (s2_start[2] + s2_end[2]) / 2
    )
    
    # Distance between midpoints
    dx = mid1[0] - mid2[0]
    dy = mid1[1] - mid2[1]
    dz = mid1[2] - mid2[2]
    
    center_distance = math.sqrt(dx*dx + dy*dy + dz*dz)
    
    # Subtract radii to get surface distance
    surface_distance = center_distance - cap1['radius'] - cap2['radius']
    
    return surface_distance

# ============================================================================


@dataclass
class RoundResult:
    """Result of a single round"""
    round_num: int
    fighter_a_score: int
    fighter_b_score: int
    fighter_a_damage_dealt: float
    fighter_b_damage_dealt: float
    fighter_a_stamina_used: float
    fighter_b_stamina_used: float
    exchanges: List[FightEvent]
    winner: str


@dataclass
class MatchResult:
    """Final result of the match"""
    winner: str
    method: str  # "Decision", "KO", "TKO"
    rounds: List[RoundResult]
    final_scores: Tuple[int, int, int]


class MuayThaiSimulatorV2:
    """
    Muay Thai match simulator that emits FightEvent objects.
    
    The simulator only handles physics and game logic. It yields events
    that describe what happened, and renderers decide how to visualize them.
    
    VERSION: v0.2.8 - Capsule collision detection
    """
    
    def __init__(self, fighter_a: Fighter, fighter_b: Fighter, real_time: bool = False):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        self.real_time = real_time
        
        # Fight state
        self.fighter_a_health = 100.0
        self.fighter_b_health = 100.0
        self.fighter_a_stamina = 100.0
        self.fighter_b_stamina = 100.0
        
        # Damage tracking by body part
        self.fighter_a_head_damage = 0.0
        self.fighter_b_head_damage = 0.0
        self.fighter_a_body_damage = 0.0
        self.fighter_b_body_damage = 0.0
        self.fighter_a_leg_damage = 0.0
        self.fighter_b_leg_damage = 0.0
        
        # Fight flow state
        self.in_clinch = False
        self.current_round = 0
        self.current_time = 0.0  # Time within current round
        
        # =====================================================
        # CAPSULE COLLISION DETECTION - NEW IN v0.2.8
        # =====================================================
        # Fighter positions (x, z coordinates - y is up)
        ##self.fighter_a_pos = {'x': -2.0, 'z': 0.0}  # Left side (red corner)
        ##self.fighter_b_pos = {'x': 2.0, 'z': 0.0}   # Right side (blue corner)

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
        #END NEW CODE


        
        # Create capsule representations
        self.capsules_a = FighterCapsules(self.fighter_a_pos, fighter_a.physical.height_cm)
        self.capsules_b = FighterCapsules(self.fighter_b_pos, fighter_b.physical.height_cm)
        
        # Collision parameters
        ##self.min_separation = 0.4  # Minimum surface distance (allows closer natural combat)
        self.min_separation = 2.0  # Minimum surface distance (allows closer natural combat)
        
    def _check_collision_capsule(self) -> bool:
        """
        Check if any capsules are colliding between fighters.
        Returns True if penetration detected.
        Uses capsule-based collision for realistic body proximity.
        """
        # Update capsule positions
        self.capsules_a.position = self.fighter_a_pos
        self.capsules_b.position = self.fighter_b_pos
        
        caps_a = self.capsules_a.get_all_capsules()
        caps_b = self.capsules_b.get_all_capsules()
        
        # Check all capsule pairs - find minimum distance
        min_distance = float('inf')
        for cap_a in caps_a:
            for cap_b in caps_b:
                dist = capsule_distance(cap_a, cap_b)
                min_distance = min(min_distance, dist)
        
        return min_distance < self.min_separation
    
    def _check_collision(self, pos1: dict, pos2: dict) -> bool:
        """
        Legacy simple collision check for testing positions.
        Used when checking potential movement.
        """
        # Temporarily update positions
        old_a = self.fighter_a_pos.copy()
        old_b = self.fighter_b_pos.copy()
        
        self.fighter_a_pos = pos1
        self.fighter_b_pos = pos2
        
        result = self._check_collision_capsule()
        
        # Restore positions
        self.fighter_a_pos = old_a
        self.fighter_b_pos = old_b
        
        return result
    
    def _resolve_collision(self):
        """
        Push fighters apart when capsules are colliding.
        Uses capsule collision data for more accurate separation.
        """
        dx = self.fighter_a_pos['x'] - self.fighter_b_pos['x']
        dz = self.fighter_a_pos['z'] - self.fighter_b_pos['z']
        
        distance = math.sqrt(dx * dx + dz * dz)
        
        if distance < 0.01:  # Avoid division by zero
            dx, dz = 1.0, 0.0
            distance = 1.0
        
        # Normalize direction vector
        dx /= distance
        dz /= distance
        
        # Calculate separation needed using torso capsules
        torso_a = self.capsules_a.get_world_capsule(self.capsules_a.torso)
        torso_b = self.capsules_b.get_world_capsule(self.capsules_b.torso)
        torso_dist = capsule_distance(torso_a, torso_b)
        
        if torso_dist < self.min_separation:
            overlap = self.min_separation - torso_dist
            separation = overlap / 2  # Push each fighter half the distance
            
            # Apply separation
            self.fighter_a_pos['x'] += dx * separation
            self.fighter_a_pos['z'] += dz * separation
            self.fighter_b_pos['x'] -= dx * separation
            self.fighter_b_pos['z'] -= dz * separation

    # NEW METHODS BEGIN

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
        4. Back to corners
        5. (Then Round 1 starts and they come out fighting)
        
        Yields StateUpdateEvent objects for position updates
        """

        print("🎯 FIST-BUMP SEQUENCE STARTING")  # ADD THIS

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

        print("🎯 Phase 2: Pause at fist-bump position")  # ADD THIS

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
        
        # Phase 3: Back to CORNERS (0.8 seconds, 8 steps) - CHANGED!

        print("🎯 Phase 3: Back to CORNERS (0.8 seconds, 8 steps")  # ADD THIS

        steps_back = 8
        
        for step in range(steps_back + 1):
            t = step / steps_back
            eased_t = self._ease_in_out(t)
            
            # Move back to corners (reverse of phase 1)
            self.fighter_a_pos['x'] = self._lerp(-bump_distance/2, self.corner_a_pos['x'], eased_t)
            self.fighter_b_pos['x'] = self._lerp(bump_distance/2, self.corner_b_pos['x'], eased_t)
            
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

        # NEW METHODS END

    def _update_fighter_movement(self):
        """
        Update fighter positions based on combat state.
        Fighters move naturally during the fight with collision prevention.
        """
        # Movement parameters (subtle, realistic motion)
        movement_speed = 0.2  # Units per update (increased for visibility)
        
        # In clinch - fighters are very close
        if self.in_clinch:
            target_distance = 0.8
            # Move fighters toward clinch distance
            dx = self.fighter_b_pos['x'] - self.fighter_a_pos['x']
            dz = self.fighter_b_pos['z'] - self.fighter_a_pos['z']
            current_distance = math.sqrt(dx * dx + dz * dz)
            
            if current_distance > target_distance:
                # Normalize and move closer
                dx /= current_distance
                dz /= current_distance
                self.fighter_a_pos['x'] += dx * movement_speed
                self.fighter_a_pos['z'] += dz * movement_speed
                self.fighter_b_pos['x'] -= dx * movement_speed
                self.fighter_b_pos['z'] -= dz * movement_speed
        else:
            # Regular striking range - fighters circle and adjust distance
            # Random subtle movement (circling, adjusting stance)
            if random.random() < 0.3:  # 30% chance to move
                angle = random.uniform(-0.3, 0.3)  # Small angle change
                
                # Move fighter A
                temp_a_pos = {
                    'x': self.fighter_a_pos['x'] + math.cos(angle) * movement_speed,
                    'z': self.fighter_a_pos['z'] + math.sin(angle) * movement_speed
                }
                
                # Move fighter B (opposite direction for now)
                temp_b_pos = {
                    'x': self.fighter_b_pos['x'] - math.cos(angle) * movement_speed,
                    'z': self.fighter_b_pos['z'] - math.sin(angle) * movement_speed
                }
                
                # Only apply movement if it doesn't cause collision
                if not self._check_collision(temp_a_pos, temp_b_pos):
                    self.fighter_a_pos = temp_a_pos
                    self.fighter_b_pos = temp_b_pos
                else:
                    # If movement would cause collision, resolve it
                    self._resolve_collision()
        
        # Keep fighters in ring bounds (optional - prevents them from drifting too far)
        ring_radius = 8.0
        for pos in [self.fighter_a_pos, self.fighter_b_pos]:
            distance_from_center = math.sqrt(pos['x'] * pos['x'] + pos['z'] * pos['z'])
            if distance_from_center > ring_radius:
                # Pull back toward center
                factor = ring_radius / distance_from_center
                pos['x'] *= factor
                pos['z'] *= factor
        
        # Final collision check and resolution using capsules
        if self._check_collision_capsule():
            self._resolve_collision()
        
    def _get_damage_degradation(self, head_dmg: float, body_dmg: float, 
                                leg_dmg: float, durability) -> dict:
        """Calculate how accumulated damage affects performance"""
        head_factor = max(0.5, 1.0 - (head_dmg / (100 * durability.head_durability / 100)) * 0.5)
        body_factor = max(0.6, 1.0 - (body_dmg / (100 * durability.body_durability / 100)) * 0.4)
        leg_factor = max(0.7, 1.0 - (leg_dmg / (100 * durability.leg_durability / 100)) * 0.3)
        
        return {
            'defense_mult': head_factor,
            'power_mult': body_factor,
            'stamina_mult': body_factor,
            'speed_mult': leg_factor
        }
    
    def _create_state_update(self) -> StateUpdateEvent:
        """
        Create a state update event with current health/stamina/damage/positions.
        Updated in v0.2.6 to include fighter positions for collision visualization.
        """
        return StateUpdateEvent(
            event_type=EventType.STATE_UPDATE,
            timestamp=self.current_time,
            round_num=self.current_round,
            fighter_a_health=self.fighter_a_health,
            fighter_b_health=self.fighter_b_health,
            fighter_a_stamina=self.fighter_a_stamina,
            fighter_b_stamina=self.fighter_b_stamina,
            fighter_a_head_damage=self.fighter_a_head_damage,
            fighter_a_body_damage=self.fighter_a_body_damage,
            fighter_a_leg_damage=self.fighter_a_leg_damage,
            fighter_b_head_damage=self.fighter_b_head_damage,
            fighter_b_body_damage=self.fighter_b_body_damage,
            fighter_b_leg_damage=self.fighter_b_leg_damage,
            # NEW: Position data
            fighter_a_pos_x=self.fighter_a_pos['x'],
            fighter_a_pos_z=self.fighter_a_pos['z'],
            fighter_b_pos_x=self.fighter_b_pos['x'],
            fighter_b_pos_z=self.fighter_b_pos['z'],
        )
    
    def _select_strike_move(self, is_power: bool, targets_body: bool, 
                            targets_legs: bool) -> Tuple[MoveType, TargetZone]:
        """Select a specific strike type based on attack parameters"""
        if targets_legs:
            return MoveType.LEG_KICK, TargetZone.LEGS
        elif targets_body:
            if is_power:
                move = random.choice([MoveType.BODY_PUNCH, MoveType.BODY_KICK, MoveType.KNEE])
            else:
                move = MoveType.BODY_PUNCH
            return move, TargetZone.BODY
        else:  # head
            if is_power:
                move = random.choice([MoveType.CROSS, MoveType.HOOK, MoveType.HEAD_KICK, MoveType.ELBOW])
            else:
                move = random.choice([MoveType.JAB, MoveType.CROSS])
            return move, TargetZone.HEAD
    
    def _determine_strike_result(self, attack_power: float, defense_power: float) -> StrikeResult:
        """Determine if a strike lands based on attack vs defense"""
        hit_chance = 0.5 + (attack_power - defense_power) / 200
        hit_chance = max(0.2, min(0.9, hit_chance))  # Clamp between 20% and 90%
        
        roll = random.random()
        if roll < hit_chance * 0.6:
            return StrikeResult.LANDED_CLEAN
        elif roll < hit_chance:
            return StrikeResult.LANDED_PARTIAL
        elif roll < hit_chance + 0.2:
            return StrikeResult.BLOCKED
        else:
            return StrikeResult.MISSED
    
    def simulate_exchange(self) -> List[FightEvent]:
        """
        Simulate a single exchange and return the events that occurred.
        An exchange might produce multiple events (strike, reaction, etc.)
        """
        events = []
        
        # Get degradation from accumulated damage
        a_degrade = self._get_damage_degradation(
            self.fighter_a_head_damage, 
            self.fighter_a_body_damage,
            self.fighter_a_leg_damage,
            self.fighter_a.durability
        )
        b_degrade = self._get_damage_degradation(
            self.fighter_b_head_damage,
            self.fighter_b_body_damage,
            self.fighter_b_leg_damage,
            self.fighter_b.durability
        )
        
        # Stamina affects effectiveness
        a_effectiveness = (self.fighter_a_stamina / 100.0) * a_degrade['stamina_mult']
        b_effectiveness = (self.fighter_b_stamina / 100.0) * b_degrade['stamina_mult']
        
        # Determine exchange type
        exchange_type = random.choice(['striking', 'clinch', 'defense', 'leg_kick'])
        
        if exchange_type == 'striking':
            events.extend(self._simulate_striking_exchange(
                a_degrade, b_degrade, a_effectiveness, b_effectiveness
            ))
        elif exchange_type == 'leg_kick':
            events.extend(self._simulate_leg_kick_exchange(
                a_degrade, b_degrade, a_effectiveness, b_effectiveness
            ))
        elif exchange_type == 'clinch':
            events.extend(self._simulate_clinch_exchange(
                a_degrade, b_degrade, a_effectiveness, b_effectiveness
            ))
        else:  # defensive
            events.extend(self._simulate_defensive_exchange(
                a_degrade, b_degrade, a_effectiveness, b_effectiveness
            ))
        
        return events
    
    def _simulate_striking_exchange(self, a_degrade: dict, b_degrade: dict,
                                    a_eff: float, b_eff: float) -> List[FightEvent]:
        """Simulate a striking exchange - both fighters throw"""
        events = []
        
        # Determine targeting
        a_targets_body = random.random() * 100 < self.fighter_a.style.body_attack_preference
        b_targets_body = random.random() * 100 < self.fighter_b.style.body_attack_preference
        
        # Power punch or regular?
        a_power = random.random() * 100 < self.fighter_a.style.power_punch_frequency
        b_power = random.random() * 100 < self.fighter_b.style.power_punch_frequency
        
        # Fighter A attacks
        a_move, a_target = self._select_strike_move(a_power, a_targets_body, False)
        a_attack_power = (self.fighter_a.stats.power * a_degrade['power_mult'] + 
                        self.fighter_a.stats.speed * a_degrade['speed_mult']) * a_eff
        b_defense_power = (self.fighter_b.stats.defense * b_degrade['defense_mult'] + 
                        self.fighter_b.stats.speed * b_degrade['speed_mult']) * b_eff
        
        a_result = self._determine_strike_result(a_attack_power, b_defense_power)
        
        if a_result in [StrikeResult.LANDED_CLEAN, StrikeResult.LANDED_PARTIAL]:
            damage_mult = 1.0 if a_result == StrikeResult.LANDED_CLEAN else 0.5
            base_damage = self.fighter_a.stats.power * a_degrade['power_mult'] * damage_mult * 0.15
            
            # Apply damage to correct body part
            if a_target == TargetZone.HEAD:
                self.fighter_b_head_damage += base_damage
            elif a_target == TargetZone.BODY:
                self.fighter_b_body_damage += base_damage
            else:
                self.fighter_b_leg_damage += base_damage
            
            self.fighter_b_health -= base_damage
            
            events.append(StrikeEvent(
                event_type=EventType.STRIKE,
                timestamp=self.current_time,
                round_num=self.current_round,
                attacker=FighterID.A,
                defender=FighterID.B,
                move_type=a_move,
                target_zone=a_target,
                result=a_result,
                damage=base_damage,
            ))
        
        # Stamina cost
        stamina_cost = 2.0 if a_power else 1.0
        self.fighter_a_stamina -= stamina_cost
        
        # Fighter B counter-attacks
        b_move, b_target = self._select_strike_move(b_power, b_targets_body, False)
        b_attack_power = (self.fighter_b.stats.power * b_degrade['power_mult'] + 
                        self.fighter_b.stats.speed * b_degrade['speed_mult']) * b_eff
        a_defense_power = (self.fighter_a.stats.defense * a_degrade['defense_mult'] + 
                        self.fighter_a.stats.speed * a_degrade['speed_mult']) * a_eff
        
        b_result = self._determine_strike_result(b_attack_power, a_defense_power)
        
        if b_result in [StrikeResult.LANDED_CLEAN, StrikeResult.LANDED_PARTIAL]:
            damage_mult = 1.0 if b_result == StrikeResult.LANDED_CLEAN else 0.5
            base_damage = self.fighter_b.stats.power * b_degrade['power_mult'] * damage_mult * 0.15
            
            # Apply damage to correct body part
            if b_target == TargetZone.HEAD:
                self.fighter_a_head_damage += base_damage
            elif b_target == TargetZone.BODY:
                self.fighter_a_body_damage += base_damage
            else:
                self.fighter_a_leg_damage += base_damage
            
            self.fighter_a_health -= base_damage
            
            events.append(StrikeEvent(
                event_type=EventType.STRIKE,
                timestamp=self.current_time,
                round_num=self.current_round,
                attacker=FighterID.B,
                defender=FighterID.A,
                move_type=b_move,
                target_zone=b_target,
                result=b_result,
                damage=base_damage,
            ))
        
        stamina_cost = 2.0 if b_power else 1.0
        self.fighter_b_stamina -= stamina_cost
        
        return events
    
    def _simulate_leg_kick_exchange(self, a_degrade: dict, b_degrade: dict,
                                    a_eff: float, b_eff: float) -> List[FightEvent]:
        """Simulate focused leg kick exchange"""
        events = []
        
        attacker = random.choice([FighterID.A, FighterID.B])
        
        if attacker == FighterID.A:
            attack_power = (self.fighter_a.stats.power * a_degrade['power_mult']) * a_eff
            defense_power = (self.fighter_b.stats.defense * b_degrade['defense_mult']) * b_eff
            result = self._determine_strike_result(attack_power, defense_power)
            
            if result in [StrikeResult.LANDED_CLEAN, StrikeResult.LANDED_PARTIAL]:
                damage_mult = 1.0 if result == StrikeResult.LANDED_CLEAN else 0.5
                base_damage = self.fighter_a.stats.power * a_degrade['power_mult'] * damage_mult * 0.12
                self.fighter_b_leg_damage += base_damage
                self.fighter_b_health -= base_damage
                
                events.append(StrikeEvent(
                    event_type=EventType.STRIKE,
                    timestamp=self.current_time,
                    round_num=self.current_round,
                    attacker=FighterID.A,
                    defender=FighterID.B,
                    move_type=MoveType.LEG_KICK,
                    target_zone=TargetZone.LEGS,
                    result=result,
                    damage=base_damage,
                ))
            
            self.fighter_a_stamina -= 1.5
        else:
            attack_power = (self.fighter_b.stats.power * b_degrade['power_mult']) * b_eff
            defense_power = (self.fighter_a.stats.defense * a_degrade['defense_mult']) * a_eff
            result = self._determine_strike_result(attack_power, defense_power)
            
            if result in [StrikeResult.LANDED_CLEAN, StrikeResult.LANDED_PARTIAL]:
                damage_mult = 1.0 if result == StrikeResult.LANDED_CLEAN else 0.5
                base_damage = self.fighter_b.stats.power * b_degrade['power_mult'] * damage_mult * 0.12
                self.fighter_a_leg_damage += base_damage
                self.fighter_a_health -= base_damage
                
                events.append(StrikeEvent(
                    event_type=EventType.STRIKE,
                    timestamp=self.current_time,
                    round_num=self.current_round,
                    attacker=FighterID.B,
                    defender=FighterID.A,
                    move_type=MoveType.LEG_KICK,
                    target_zone=TargetZone.LEGS,
                    result=result,
                    damage=base_damage,
                ))
            
            self.fighter_b_stamina -= 1.5
        
        return events
    
    def _simulate_clinch_exchange(self, a_degrade: dict, b_degrade: dict,
                                a_eff: float, b_eff: float) -> List[FightEvent]:
        """Simulate clinch battle"""
        events = []
        
        if not self.in_clinch:
            # Enter clinch
            self.in_clinch = True
            events.append(ClinchEvent(
                event_type=EventType.CLINCH,
                timestamp=self.current_time,
                round_num=self.current_round,
                initiator=random.choice([FighterID.A, FighterID.B]),
            ))
        
        # Clinch damage
        a_clinch_power = self.fighter_a.stats.clinch * a_degrade['power_mult'] * a_eff
        b_clinch_power = self.fighter_b.stats.clinch * b_degrade['power_mult'] * b_eff
        
        if a_clinch_power > b_clinch_power:
            damage = (a_clinch_power - b_clinch_power) * 0.1
            self.fighter_b_body_damage += damage
            self.fighter_b_health -= damage
            
            events.append(StrikeEvent(
                event_type=EventType.STRIKE,
                timestamp=self.current_time,
                round_num=self.current_round,
                attacker=FighterID.A,
                defender=FighterID.B,
                move_type=MoveType.KNEE,
                target_zone=TargetZone.BODY,
                result=StrikeResult.LANDED_CLEAN,
                damage=damage,
            ))
        else:
            damage = (b_clinch_power - a_clinch_power) * 0.1
            self.fighter_a_body_damage += damage
            self.fighter_a_health -= damage
            
            events.append(StrikeEvent(
                event_type=EventType.STRIKE,
                timestamp=self.current_time,
                round_num=self.current_round,
                attacker=FighterID.B,
                defender=FighterID.A,
                move_type=MoveType.KNEE,
                target_zone=TargetZone.BODY,
                result=StrikeResult.LANDED_CLEAN,
                damage=damage,
            ))
        
        # Clinch costs stamina
        self.fighter_a_stamina -= 2.0
        self.fighter_b_stamina -= 2.0
        
        # Random clinch exit
        if random.random() < 0.4:
            self.in_clinch = False
            events.append(ClinchExitEvent(
                event_type=EventType.CLINCH_EXIT,
                timestamp=self.current_time,
                round_num=self.current_round,
            ))
        
        return events
    
    def _simulate_defensive_exchange(self, a_degrade: dict, b_degrade: dict,
                                    a_eff: float, b_eff: float) -> List[FightEvent]:
        """Simulate a more defensive exchange - less action"""
        events = []
        
        # One fighter attempts, other defends well
        attacker = random.choice([FighterID.A, FighterID.B])
        
        if attacker == FighterID.A:
            attack_power = (self.fighter_a.stats.power * a_degrade['power_mult']) * a_eff * 0.7
            defense_power = (self.fighter_b.stats.defense * b_degrade['defense_mult']) * b_eff * 1.3
        else:
            attack_power = (self.fighter_b.stats.power * b_degrade['power_mult']) * b_eff * 0.7
            defense_power = (self.fighter_a.stats.defense * a_degrade['defense_mult']) * a_eff * 1.3
        
        result = self._determine_strike_result(attack_power, defense_power)
        
        # Defensive exchanges usually result in blocks/misses
        if result == StrikeResult.LANDED_CLEAN:
            result = StrikeResult.LANDED_PARTIAL  # Downgrade
        
        # Only small stamina cost
        if attacker == FighterID.A:
            self.fighter_a_stamina -= 0.5
        else:
            self.fighter_b_stamina -= 0.5
        
        return events
    
    def simulate_round_streaming(self, round_num: int) -> Generator[FightEvent, None, RoundResult]:
        """
        Generator that yields all events for a single round.
        Returns RoundResult when complete.
        
        Updated in v0.2.6 to include fighter movement and collision detection.
        """
        self.current_round = round_num
        self.current_time = 0.0


        # NEW CODE BEGIN
        # ADD THIS: Reset positions to combat stance at start of each round
        self.fighter_a_pos = self.combat_a_pos.copy()
        self.fighter_b_pos = self.combat_b_pos.copy()
        # NEW CODE END


        all_events = []
        
        starting_a_health = self.fighter_a_health
        starting_b_health = self.fighter_b_health
        
        # Round start
        yield RoundStartEvent(
            event_type=EventType.ROUND_START,
            timestamp=0,
            round_num=round_num,
        )
        
        # Simulate round (3 minutes = 180 seconds, or shortened for demo)
        round_duration = 180 if self.real_time else 20
        exchanges_per_round = 30
        time_per_exchange = round_duration / exchanges_per_round
        
        for _ in range(exchanges_per_round):
            self.current_time += time_per_exchange
            
            # =====================================================
            # UPDATE FIGHTER MOVEMENT (NEW IN v0.2.6)
            # =====================================================
            self._update_fighter_movement()
            
            # Simulate exchange
            events = self.simulate_exchange()
            all_events.extend(events)
            
            # Yield each event
            for event in events:
                yield event
            
            # Apply stamina floor
            self.fighter_a_stamina = max(20, self.fighter_a_stamina)
            self.fighter_b_stamina = max(20, self.fighter_b_stamina)
            
            # Yield state update (now includes positions)
            yield self._create_state_update()
            
            # Check for knockdown (health below threshold mid-round)
            if self.fighter_a_health < 30 and self.fighter_a_health > 20:
                yield KnockdownEvent(
                    event_type=EventType.KNOCKDOWN,
                    timestamp=self.current_time,
                    round_num=round_num,
                    fighter=FighterID.A,
                    cause=MoveType.CROSS,  # Simplified - could track actual cause
                )
                # Recovery
                yield RecoveryEvent(
                    event_type=EventType.RECOVERY,
                    timestamp=self.current_time - 2,
                    round_num=round_num,
                    fighter=FighterID.A,
                )
            
            if self.fighter_b_health < 30 and self.fighter_b_health > 20:
                yield KnockdownEvent(
                    event_type=EventType.KNOCKDOWN,
                    timestamp=self.current_time,
                    round_num=round_num,
                    fighter=FighterID.B,
                    cause=MoveType.CROSS,
                )
                yield RecoveryEvent(
                    event_type=EventType.RECOVERY,
                    timestamp=self.current_time - 2,
                    round_num=round_num,
                    fighter=FighterID.B,
                )
        
        # Calculate round damage
        a_round_damage = starting_a_health - self.fighter_a_health
        b_round_damage = starting_b_health - self.fighter_b_health
        
        # Score the round (10-point must system)
        # Note: damage dealt TO opponent, so b_round_damage means A did well
        if b_round_damage > a_round_damage * 1.3:
            a_score, b_score = 10, 9
            winner = self.fighter_a.name
        elif a_round_damage > b_round_damage * 1.3:
            a_score, b_score = 9, 10
            winner = self.fighter_b.name
        elif b_round_damage > a_round_damage:
            a_score, b_score = 10, 9
            winner = self.fighter_a.name
        elif a_round_damage > b_round_damage:
            a_score, b_score = 9, 10
            winner = self.fighter_b.name
        else:
            a_score, b_score = 10, 10
            winner = "Draw"
        
        # Round end event
        yield RoundEndEvent(
            event_type=EventType.ROUND_END,
            timestamp=0,
            round_num=round_num,
            fighter_a_score=a_score,
            fighter_b_score=b_score,
            winner_name=winner,
        )
        
        # Recovery between rounds
        a_recovery = self.fighter_a.durability.recovery_rate / 100.0
        b_recovery = self.fighter_b.durability.recovery_rate / 100.0
        
        self.fighter_a_stamina = min(100, self.fighter_a_stamina + (15 * a_recovery))
        self.fighter_b_stamina = min(100, self.fighter_b_stamina + (15 * b_recovery))
        
        # Partial damage recovery
        self.fighter_a_head_damage = max(0, self.fighter_a_head_damage - (2 * a_recovery))
        self.fighter_b_head_damage = max(0, self.fighter_b_head_damage - (2 * b_recovery))
        self.fighter_a_body_damage = max(0, self.fighter_a_body_damage - (3 * a_recovery))
        self.fighter_b_body_damage = max(0, self.fighter_b_body_damage - (3 * b_recovery))
        self.fighter_a_leg_damage = max(0, self.fighter_a_leg_damage - (2 * a_recovery))
        self.fighter_b_leg_damage = max(0, self.fighter_b_leg_damage - (2 * b_recovery))
        
        return RoundResult(
            round_num=round_num,
            fighter_a_score=a_score,
            fighter_b_score=b_score,
            fighter_a_damage_dealt=b_round_damage,
            fighter_b_damage_dealt=a_round_damage,
            fighter_a_stamina_used=100 - self.fighter_a_stamina,
            fighter_b_stamina_used=100 - self.fighter_b_stamina,
            exchanges=all_events,
            winner=winner,
        )
        
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
        
        # CRITICAL FIX: Reset fighters to combat positions after fist-bump
        # The fist-bump moves them back to corners, but combat needs them closer
        self.fighter_a_pos = self.combat_a_pos.copy()
        self.fighter_b_pos = self.combat_b_pos.copy()
        
        # Update capsule positions for collision detection
        self.capsules_a.position = self.fighter_a_pos
        self.capsules_b.position = self.fighter_b_pos

        
        for round_num in range(1, 6):
            # Simulate round
            round_gen = self.simulate_round_streaming(round_num)
            
            # Yield all round events
            try:
                while True:
                    event = next(round_gen)
                    yield event
            except StopIteration as e:
                round_result = e.value
                rounds.append(round_result)
            
            # Check for TKO
            if self.fighter_a_health < 20:
                yield MatchEndEvent(
                    event_type=EventType.MATCH_END,
                    timestamp=0,
                    round_num=round_num,
                    winner_name=self.fighter_b.name,
                    method=f"TKO Round {round_num}",
                    fighter_a_total_score=0,
                    fighter_b_total_score=0,
                )
                return MatchResult(
                    winner=self.fighter_b.name,
                    method=f"TKO Round {round_num}",
                    rounds=rounds,
                    final_scores=(0, 0, 0),
                )
            
            if self.fighter_b_health < 20:
                yield MatchEndEvent(
                    event_type=EventType.MATCH_END,
                    timestamp=0,
                    round_num=round_num,
                    winner_name=self.fighter_a.name,
                    method=f"TKO Round {round_num}",
                    fighter_a_total_score=0,
                    fighter_b_total_score=0,
                )
                return MatchResult(
                    winner=self.fighter_a.name,
                    method=f"TKO Round {round_num}",
                    rounds=rounds,
                    final_scores=(0, 0, 0),
                )
            
            # Break between rounds (except after round 5)
            if round_num < 5:
                yield BreakStartEvent(
                    event_type=EventType.BREAK_START,
                    timestamp=0,
                    round_num=round_num,
                    duration_seconds=60 if self.real_time else 2,
                )
        
        # Calculate final scores
        a_total = sum(r.fighter_a_score for r in rounds)
        b_total = sum(r.fighter_b_score for r in rounds)
        
        if a_total > b_total:
            winner = self.fighter_a.name
            method = f"Decision ({a_total}-{b_total})"
        elif b_total > a_total:
            winner = self.fighter_b.name
            method = f"Decision ({b_total}-{a_total})"
        else:
            winner = "Draw"
            method = f"Draw ({a_total}-{a_total})"
        
        yield MatchEndEvent(
            event_type=EventType.MATCH_END,
            timestamp=0,
            round_num=5,
            winner_name=winner,
            method=method,
            fighter_a_total_score=a_total,
            fighter_b_total_score=b_total,
        )
        
        return MatchResult(
            winner=winner,
            method=method,
            rounds=rounds,
            final_scores=(a_total, a_total, a_total),
        )
