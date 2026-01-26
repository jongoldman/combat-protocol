# renderer_2d.py
"""
2D Canvas/SVG renderer for Combat Protocol.

This renderer uses simple 2D silhouettes with pose swapping.
Designed to work both in browser (via JSON output) and could be
adapted for terminal with ASCII art.
"""

import os
from typing import Dict, Any, Optional
from dataclasses import dataclass
from events import (
    FightEvent, EventType, FighterID, MoveType,
    MatchStartEvent, RoundStartEvent, StrikeEvent, ClinchEvent,
    KnockdownEvent, StateUpdateEvent, RoundEndEvent, MatchEndEvent,
    CommentaryEvent, BreakStartEvent, ClinchExitEvent, RecoveryEvent
)
from renderer import Renderer, FightVisualState, FighterVisualState, RendererFactory


# Pose definitions for 2D silhouettes
# Each pose maps to a sprite/SVG or a CSS class
POSE_DEFINITIONS = {
    'idle': {
        'duration': 0.0,  # Stays until changed
        'sprite': 'idle',
        'description': 'Fighting stance',
    },
    'jab': {
        'duration': 0.3,
        'sprite': 'punch_straight',
        'description': 'Quick jab',
    },
    'cross': {
        'duration': 0.4,
        'sprite': 'punch_straight',
        'description': 'Power cross',
    },
    'hook': {
        'duration': 0.4,
        'sprite': 'punch_hook',
        'description': 'Hook punch',
    },
    'uppercut': {
        'duration': 0.4,
        'sprite': 'punch_upper',
        'description': 'Uppercut',
    },
    'body_punch': {
        'duration': 0.35,
        'sprite': 'punch_body',
        'description': 'Body shot',
    },
    'leg_kick': {
        'duration': 0.5,
        'sprite': 'kick_low',
        'description': 'Leg kick',
    },
    'body_kick': {
        'duration': 0.5,
        'sprite': 'kick_mid',
        'description': 'Body kick',
    },
    'head_kick': {
        'duration': 0.6,
        'sprite': 'kick_high',
        'description': 'Head kick',
    },
    'knee': {
        'duration': 0.4,
        'sprite': 'knee',
        'description': 'Knee strike',
    },
    'elbow': {
        'duration': 0.35,
        'sprite': 'elbow',
        'description': 'Elbow strike',
    },
    'clinch': {
        'duration': 0.0,  # Stays until clinch exit
        'sprite': 'clinch',
        'description': 'In clinch',
    },
    'throw': {
        'duration': 0.8,
        'sprite': 'throw',
        'description': 'Clinch throw',
    },
    'block': {
        'duration': 0.3,
        'sprite': 'block',
        'description': 'Blocking',
    },
    'slip': {
        'duration': 0.3,
        'sprite': 'slip',
        'description': 'Slipping punch',
    },
    'parry': {
        'duration': 0.25,
        'sprite': 'parry',
        'description': 'Parrying',
    },
    'check': {
        'duration': 0.4,
        'sprite': 'check',
        'description': 'Checking kick',
    },
    'hurt': {
        'duration': 0.4,
        'sprite': 'hurt',
        'description': 'Taking damage',
    },
    'knockdown': {
        'duration': 2.0,
        'sprite': 'knockdown',
        'description': 'Knocked down',
    },
    'getting_up': {
        'duration': 1.0,
        'sprite': 'getting_up',
        'description': 'Recovering',
    },
}


class Renderer2D(Renderer):
    """
    2D sprite-based renderer.
    
    Outputs JSON that the browser interprets to update Canvas/DOM.
    This keeps the Python side simple and lets the browser handle
    actual drawing and animation interpolation.
    """
    
    def __init__(self):
        super().__init__()
        self.current_time: float = 0.0
        self.config: Dict[str, Any] = {}
        self.fighter_a_id: Optional[str] = None
        self.fighter_b_id: Optional[str] = None
    
    def init(self, fighter_a_name: str, fighter_b_name: str, config: Dict[str, Any] = None) -> None:
        """Initialize the 2D renderer"""
        self.fighter_a_name = fighter_a_name
        self.fighter_b_name = fighter_b_name
        self.config = config or {}
        
        # Store fighter IDs if provided in config
        self.fighter_a_id = config.get('fighter_a_id') if config else None
        self.fighter_b_id = config.get('fighter_b_id') if config else None
        
        self.state = self._init_visual_state(fighter_a_name, fighter_b_name)
        self.current_time = 0.0
    
    def handle_event(self, event: FightEvent) -> None:
        """Process fight events and update visual state"""
        
        if isinstance(event, MatchStartEvent):
            self._handle_match_start(event)
        elif isinstance(event, RoundStartEvent):
            self._handle_round_start(event)
        elif isinstance(event, StrikeEvent):
            self._handle_strike(event)
        elif isinstance(event, ClinchEvent):
            self._handle_clinch(event)
        elif isinstance(event, ClinchExitEvent):
            self._handle_clinch_exit(event)
        elif isinstance(event, KnockdownEvent):
            self._handle_knockdown(event)
        elif isinstance(event, RecoveryEvent):
            self._handle_recovery(event)
        elif isinstance(event, StateUpdateEvent):
            self._handle_state_update(event)
        elif isinstance(event, RoundEndEvent):
            self._handle_round_end(event)
        elif isinstance(event, MatchEndEvent):
            self._handle_match_end(event)
        elif isinstance(event, CommentaryEvent):
            self._handle_commentary(event)
        elif isinstance(event, BreakStartEvent):
            self._handle_break(event)
    
    def _handle_match_start(self, event: MatchStartEvent) -> None:
        """Reset state for new match"""
        self.state = self._init_visual_state(event.fighter_a_name, event.fighter_b_name)
    
    def _handle_round_start(self, event: RoundStartEvent) -> None:
        """Start of a new round"""
        self.state.round_num = event.round_num
        self.state.time_remaining = 180.0
        self.state.is_in_clinch = False
        
        # Reset to idle poses
        self.state.fighter_a.pose = 'idle'
        self.state.fighter_b.pose = 'idle'
        self.state.fighter_a.is_down = False
        self.state.fighter_b.is_down = False
    
    def _handle_strike(self, event: StrikeEvent) -> None:
        """Process a strike event"""
        attacker = self._get_fighter_state(event.attacker)
        defender = self._get_fighter_state(event.defender)
        
        # Set attacker pose
        attacker_pose = self._map_move_to_pose(event.move_type.name)  # Changed from event.move
        attacker.pose = attacker_pose
        attacker.pose_start_time = self.current_time
        attacker.pose_duration = POSE_DEFINITIONS.get(attacker_pose, {}).get('duration', 0.4)
        attacker.is_attacking = True
        
        # Set defender reaction based on result
        defender_reaction = self._map_result_to_reaction(event.result.name)
        if defender_reaction != 'idle':
            defender.pose = defender_reaction
            defender.pose_start_time = self.current_time
            defender.pose_duration = POSE_DEFINITIONS.get(defender_reaction, {}).get('duration', 0.3)
            defender.is_hurt = (defender_reaction == 'hurt')
        
        # Build action description
        self.state.last_action = self._build_strike_description(event, attacker.name, defender.name)
    
    def _handle_clinch(self, event: ClinchEvent) -> None:
        """Process clinch events"""
        initiator = self._get_fighter_state(event.initiator)
        other = self._get_fighter_state(
            FighterID.B if event.initiator == FighterID.A else FighterID.A
        )
        
        if event.move == MoveType.CLINCH_ENTRY:
            # Both fighters enter clinch pose
            self.state.is_in_clinch = True
            initiator.pose = 'clinch'
            initiator.in_clinch = True
            other.pose = 'clinch'
            other.in_clinch = True
            self.state.last_action = f"{initiator.name} locks up {other.name} in the clinch"
        else:
            # Clinch strike (knee, elbow)
            pose = self._map_move_to_pose(event.move.name)
            initiator.pose = pose
            initiator.pose_start_time = self.current_time
            initiator.pose_duration = POSE_DEFINITIONS.get(pose, {}).get('duration', 0.4)
            
            if event.result.name in ('LANDED_CLEAN', 'LANDED_PARTIAL'):
                other.pose = 'hurt'
                other.pose_start_time = self.current_time
                other.pose_duration = 0.3
                
                # Brutal clinch descriptions
                move_desc = "knee" if event.move == MoveType.CLINCH_KNEE else "elbow"
                brutal_clinch = [
                    f"{initiator.name} DRIVES a brutal {move_desc} into {other.name}!",
                    f"Devastating {move_desc} in the clinch from {initiator.name}!",
                    f"{initiator.name} punishes {other.name} with a vicious {move_desc}!",
                ]
                import random
                self.state.last_action = random.choice(brutal_clinch)
            else:
                self.state.last_action = f"{initiator.name} misses in the clinch"
    
    def _handle_clinch_exit(self, event: ClinchExitEvent) -> None:
        """Exit the clinch"""
        self.state.is_in_clinch = False
        self.state.fighter_a.in_clinch = False
        self.state.fighter_b.in_clinch = False
        self.state.fighter_a.pose = 'idle'
        self.state.fighter_b.pose = 'idle'
        
        breaker = self._get_fighter_state(event.breaker)
        self.state.last_action = f"{breaker.name} breaks from the clinch"
    
    def _handle_knockdown(self, event: KnockdownEvent) -> None:
        """Fighter gets dropped"""
        fighter = self._get_fighter_state(event.fighter)
        fighter.pose = 'knockdown'
        fighter.pose_start_time = self.current_time
        fighter.pose_duration = 2.0
        fighter.is_down = True
        
        # Brutal knockdown descriptions
        knockdown_descriptions = [
            f"{fighter.name} is DOWN! BRUTAL knockdown!",
            f"{fighter.name} CRUMBLES to the canvas!",
            f"OH MY GOD! {fighter.name} is OUT ON THEIR FEET!",
            f"DEVASTATING! {fighter.name} goes DOWN HARD!",
            f"{fighter.name} is DROPPED! This could be over!",
        ]
        import random
        self.state.last_action = random.choice(knockdown_descriptions)
    
    def _handle_recovery(self, event: RecoveryEvent) -> None:
        """Fighter gets back up"""
        fighter = self._get_fighter_state(event.fighter)
        fighter.pose = 'getting_up'
        fighter.pose_start_time = self.current_time
        fighter.pose_duration = 1.0
        fighter.is_down = False
        
        # Dramatic recovery descriptions
        recovery_descriptions = [
            f"{fighter.name} beats the count! Still in this fight!",
            f"{fighter.name} survives! Showing incredible heart!",
            f"Unbelievable! {fighter.name} gets back up!",
            f"{fighter.name} refuses to quit! What a warrior!",
        ]
        import random
        self.state.last_action = random.choice(recovery_descriptions)
    
    def _handle_state_update(self, event: StateUpdateEvent) -> None:
        """Update health/stamina/damage values"""
        self.state.fighter_a.health = event.fighter_a_health
        self.state.fighter_b.health = event.fighter_b_health
        self.state.fighter_a.stamina = event.fighter_a_stamina
        self.state.fighter_b.stamina = event.fighter_b_stamina
        
        self.state.fighter_a.head_damage = event.fighter_a_head_damage
        self.state.fighter_a.body_damage = event.fighter_a_body_damage
        self.state.fighter_a.leg_damage = event.fighter_a_leg_damage
        self.state.fighter_b.head_damage = event.fighter_b_head_damage
        self.state.fighter_b.body_damage = event.fighter_b_body_damage
        self.state.fighter_b.leg_damage = event.fighter_b_leg_damage
    
    def _handle_round_end(self, event: RoundEndEvent) -> None:
        """End of round"""
        self.state.fighter_a_round_score = event.fighter_a_score
        self.state.fighter_b_round_score = event.fighter_b_score
        self.state.last_action = f"Round {event.round_num} ends - {event.winner_name} takes the round"
    
    def _handle_match_end(self, event: MatchEndEvent) -> None:
        """Match is over"""
        self.state.fighter_a_total_score = event.fighter_a_total_score
        self.state.fighter_b_total_score = event.fighter_b_total_score
        self.state.last_action = f"WINNER: {event.winner_name} by {event.method}"
    
    def _handle_commentary(self, event: CommentaryEvent) -> None:
        """Add commentary to queue"""
        self.state.commentary.append(event.text)
    
    def _handle_break(self, event: BreakStartEvent) -> None:
        """Rest between rounds"""
        self.state.is_paused = True
        self.state.last_action = "Rest period between rounds"
    
    def _build_strike_description(self, event: StrikeEvent, attacker_name: str, defender_name: str) -> str:
        """Build a human-readable description of a strike"""
        move_names = {
            'JAB': 'jab',
            'CROSS': 'cross',
            'HOOK': 'hook',
            'UPPERCUT': 'uppercut',
            'BODY_PUNCH': 'body shot',
            'LEG_KICK': 'leg kick',
            'BODY_KICK': 'body kick',
            'HEAD_KICK': 'head kick',
            'KNEE': 'knee',
            'ELBOW': 'elbow',
        }
        move = move_names.get(event.move_type.name, event.move_type.name.lower())  # Changed from event.move
        
        # R-rated, brutal descriptions
        result_templates = {
            'LANDED_CLEAN': [
                f"{attacker_name} CRUSHES {defender_name} with a vicious {move}",
                f"{attacker_name} lands a devastating {move}",
                f"Brutal {move} from {attacker_name} rocks {defender_name}",
                f"{attacker_name} connects hard with a {move}",
            ],
            'LANDED_PARTIAL': [
                f"{attacker_name} grazes {defender_name} with a {move}",
                f"Glancing {move} from {attacker_name}",
                f"{defender_name} partially deflects the {move}",
            ],
            'BLOCKED': [
                f"{defender_name} blocks the {move}",
                f"{defender_name} absorbs the {move} on their guard",
                f"Good defense from {defender_name}",
            ],
            'MISSED': [
                f"{attacker_name} swings and misses with a {move}",
                f"Wild {move} misses the target",
                f"{defender_name} evades the {move}",
            ],
            'CHECKED': [
                f"{defender_name} checks the {move}",
                f"Good check from {defender_name}",
                f"{defender_name} shuts down the {move}",
            ],
        }
        
        result_name = event.result.name
        templates = result_templates.get(result_name, [f"{attacker_name} throws a {move}"])
        
        # Pick a template
        import random
        desc = random.choice(templates) if isinstance(templates, list) else templates
        
        # Power shots get even more brutal
        if event.is_power_shot and result_name == 'LANDED_CLEAN':
            power_variants = [
                f"DEVASTATING {move.upper()} from {attacker_name}!",
                f"{attacker_name} UNLOADS a massive {move}!",
                f"HUGE {move.upper()} rocks {defender_name}!",
                f"{attacker_name} throws EVERYTHING into that {move}!",
            ]
            desc = random.choice(power_variants)
        
        return desc
    
    def render(self, delta_time: float) -> Dict[str, Any]:
        """
        Render current frame as JSON for the browser.
        
        The browser will use this data to update Canvas/DOM.
        """
        self.current_time += delta_time
        
        # Check if poses should return to idle
        self._update_poses()
        
        # Build render output
        return {
            'type': 'frame',
            'round_num': self.state.round_num,
            'time_remaining': self._format_time(self.state.time_remaining),
            
            'fighter_a': self._render_fighter(self.state.fighter_a, facing='right'),
            'fighter_b': self._render_fighter(self.state.fighter_b, facing='left'),
            
            'scores': {
                'round': {
                    'a': self.state.fighter_a_round_score,
                    'b': self.state.fighter_b_round_score,
                },
                'total': {
                    'a': self.state.fighter_a_total_score,
                    'b': self.state.fighter_b_total_score,
                },
            },
            
            'is_in_clinch': self.state.is_in_clinch,
            'action': self.state.last_action,
            'commentary': self.state.commentary[-3:] if self.state.commentary else [],
        }
    
    def _get_fighter_image_url(self, fighter_id: Optional[str]) -> Optional[str]:
        """Check if a custom fighter image exists, return URL if found"""
        if not fighter_id:
            return None
        
        # Check if custom image exists
        image_path = f"static/images/fighters/{fighter_id}.png"
        if os.path.exists(image_path):
            return f"/static/images/fighters/{fighter_id}.png"
        
        return None
    
    def _render_fighter(self, fighter: FighterVisualState, facing: str) -> Dict[str, Any]:
        """Render a single fighter's state"""
        # Determine which fighter this is and get their custom image if available
        fighter_id = self.fighter_a_id if fighter == self.state.fighter_a else self.fighter_b_id
        image_url = self._get_fighter_image_url(fighter_id)
        
        result = {
            'name': fighter.name,
            'pose': fighter.pose,
            'sprite': POSE_DEFINITIONS.get(fighter.pose, {}).get('sprite', 'idle'),
            'facing': facing,
            'x': fighter.x,
            'y': fighter.y,
            'health': fighter.health,
            'stamina': fighter.stamina,
            'head_damage': fighter.head_damage,
            'body_damage': fighter.body_damage,
            'leg_damage': fighter.leg_damage,
            'is_attacking': fighter.is_attacking,
            'is_hurt': fighter.is_hurt,
            'is_down': fighter.is_down,
            'in_clinch': fighter.in_clinch,
        }
        
        # Add custom image URL if available
        if image_url:
            result['image_url'] = image_url
        
        return result
    
    def _update_poses(self) -> None:
        """Check if timed poses should return to idle"""
        for fighter in [self.state.fighter_a, self.state.fighter_b]:
            if fighter.pose_duration > 0:
                elapsed = self.current_time - fighter.pose_start_time
                if elapsed >= fighter.pose_duration:
                    # Return to idle (or clinch if in clinch)
                    if fighter.in_clinch:
                        fighter.pose = 'clinch'
                    else:
                        fighter.pose = 'idle'
                    fighter.is_attacking = False
                    fighter.is_hurt = False
    
    def _format_time(self, seconds: float) -> str:
        """Format seconds as M:SS"""
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}:{secs:02d}"
    
    def destroy(self) -> None:
        """Clean up"""
        self.state = None


# Register with factory
RendererFactory.register('2d', Renderer2D)
