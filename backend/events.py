# events.py
"""
Fight event protocol for Combat Protocol.

This module defines the structured events that flow from the simulator
to the renderer. By decoupling simulation from rendering, we can swap
renderers (2D sprites, 3D models, terminal ASCII) without changing
the simulation logic.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, Dict, Any


class FighterID(Enum):
    """Identifies which fighter"""
    A = auto()
    B = auto()


class MoveType(Enum):
    """Categories of fighting moves"""
    JAB = auto()
    CROSS = auto()
    HOOK = auto()
    UPPERCUT = auto()
    BODY_PUNCH = auto()
    LEG_KICK = auto()
    BODY_KICK = auto()
    HEAD_KICK = auto()
    KNEE = auto()
    ELBOW = auto()
    CLINCH_ENTRY = auto()
    CLINCH_KNEE = auto()
    CLINCH_ELBOW = auto()
    CLINCH_THROW = auto()
    BLOCK = auto()
    SLIP = auto()
    PARRY = auto()
    CHECK = auto()  # checking a leg kick


class TargetZone(Enum):
    """Where the strike is aimed"""
    HEAD = auto()
    BODY = auto()
    LEGS = auto()


class StrikeResult(Enum):
    """Outcome of a strike attempt"""
    LANDED_CLEAN = auto()    # Full damage
    LANDED_PARTIAL = auto()  # Partially blocked/glancing
    BLOCKED = auto()         # Defended successfully
    MISSED = auto()          # Whiffed
    CHECKED = auto()         # Leg kick was checked


class EventType(Enum):
    """All possible event types"""
    # Match flow
    MATCH_START = auto()
    ROUND_START = auto()
    ROUND_END = auto()
    BREAK_START = auto()
    MATCH_END = auto()
    
    # Combat actions
    STRIKE = auto()
    CLINCH = auto()
    CLINCH_EXIT = auto()
    KNOCKDOWN = auto()
    RECOVERY = auto()  # Getting up from knockdown
    
    # State updates
    STATE_UPDATE = auto()  # Health/stamina changes
    
    # Meta
    COMMENTARY = auto()  # For LLM-generated commentary


@dataclass
class FightEvent:
    """Base class for all fight events"""
    event_type: EventType
    timestamp: float  # Seconds into the round
    round_num: int
    
    # Optional metadata for extensibility
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class MatchStartEvent(FightEvent):
    """Signals the beginning of a match"""
    fighter_a_name: str = ""
    fighter_b_name: str = ""
    
    def __post_init__(self):
        self.event_type = EventType.MATCH_START


@dataclass
class RoundStartEvent(FightEvent):
    """Signals the beginning of a round"""
    
    def __post_init__(self):
        self.event_type = EventType.ROUND_START


@dataclass
class StrikeEvent(FightEvent):
    """A strike attempt (punch, kick, elbow, knee)"""
    attacker: FighterID = FighterID.A
    defender: FighterID = FighterID.B
    move_type: MoveType = MoveType.JAB  # Changed from 'move' to 'move_type'
    target_zone: TargetZone = TargetZone.HEAD  # Changed from 'target' to 'target_zone'
    result: StrikeResult = StrikeResult.LANDED_CLEAN
    damage: float = 0.0
    is_power_shot: bool = False  # Was this a loaded-up power strike?
    
    def __post_init__(self):
        self.event_type = EventType.STRIKE


@dataclass
class ClinchEvent(FightEvent):
    """Clinch engagement or action within clinch"""
    initiator: FighterID = FighterID.A
    move: MoveType = MoveType.CLINCH_ENTRY
    result: StrikeResult = StrikeResult.LANDED_CLEAN
    damage: float = 0.0
    
    def __post_init__(self):
        self.event_type = EventType.CLINCH


@dataclass  
class ClinchExitEvent(FightEvent):
    """Breaking from the clinch"""
    breaker: FighterID = FighterID.A  # Who initiated the break
    
    def __post_init__(self):
        self.event_type = EventType.CLINCH_EXIT


@dataclass
class KnockdownEvent(FightEvent):
    """A fighter gets knocked down"""
    fighter: FighterID = FighterID.A  # Who got dropped
    cause: MoveType = MoveType.CROSS  # What dropped them
    
    def __post_init__(self):
        self.event_type = EventType.KNOCKDOWN


@dataclass
class RecoveryEvent(FightEvent):
    """A fighter recovers from knockdown"""
    fighter: FighterID = FighterID.A
    
    def __post_init__(self):
        self.event_type = EventType.RECOVERY


@dataclass
class StateUpdateEvent(FightEvent):
    """Periodic state update with current health/stamina"""
    fighter_a_health: float = 100.0
    fighter_b_health: float = 100.0
    fighter_a_stamina: float = 100.0
    fighter_b_stamina: float = 100.0
    
    # Accumulated damage by zone (for visual damage effects)
    fighter_a_head_damage: float = 0.0
    fighter_a_body_damage: float = 0.0
    fighter_a_leg_damage: float = 0.0
    fighter_b_head_damage: float = 0.0
    fighter_b_body_damage: float = 0.0
    fighter_b_leg_damage: float = 0.0
    
    # NEW in v0.2.6: Fighter positions for collision detection
    fighter_a_pos_x: float = 0.0
    fighter_a_pos_z: float = 0.0
    fighter_b_pos_x: float = 0.0
    fighter_b_pos_z: float = 0.0
    
    def __post_init__(self):
        self.event_type = EventType.STATE_UPDATE


@dataclass
class RoundEndEvent(FightEvent):
    """Signals the end of a round"""
    fighter_a_score: int = 10
    fighter_b_score: int = 10
    winner_name: str = ""
    
    def __post_init__(self):
        self.event_type = EventType.ROUND_END


@dataclass
class BreakStartEvent(FightEvent):
    """Rest period between rounds"""
    duration_seconds: int = 60
    
    def __post_init__(self):
        self.event_type = EventType.BREAK_START


@dataclass
class MatchEndEvent(FightEvent):
    """Final result of the match"""
    winner_name: str = ""
    method: str = ""  # "KO", "TKO", "Decision", "Draw"
    fighter_a_total_score: int = 0
    fighter_b_total_score: int = 0
    
    def __post_init__(self):
        self.event_type = EventType.MATCH_END


@dataclass
class CommentaryEvent(FightEvent):
    """LLM-generated commentary (async, doesn't block simulation)"""
    text: str = ""
    speaker: str = "commentator"  # Could be "corner_a", "corner_b", etc.
    
    def __post_init__(self):
        self.event_type = EventType.COMMENTARY


# Helper function to serialize events for JSON transport
def event_to_dict(event: FightEvent) -> Dict[str, Any]:
    """Convert a FightEvent to a JSON-serializable dict"""
    result = {
        'event_type': event.event_type.name,
        'timestamp': event.timestamp,
        'round_num': event.round_num,
    }
    
    # Add type-specific fields
    if isinstance(event, StrikeEvent):
        result.update({
            'attacker': event.attacker.name,
            'defender': event.defender.name,
            'move': event.move_type.name,  # Serialize as 'move' for backwards compatibility
            'target': event.target_zone.name,  # Serialize as 'target' for backwards compatibility
            'result': event.result.name,
            'damage': event.damage,
            'is_power_shot': event.is_power_shot,
        })
    elif isinstance(event, ClinchEvent):
        result.update({
            'initiator': event.initiator.name,
            'move': event.move.name,
            'result': event.result.name,
            'damage': event.damage,
        })
    elif isinstance(event, KnockdownEvent):
        result.update({
            'fighter': event.fighter.name,
            'cause': event.cause.name,
        })
    elif isinstance(event, StateUpdateEvent):
        result.update({
            'fighter_a_health': event.fighter_a_health,
            'fighter_b_health': event.fighter_b_health,
            'fighter_a_stamina': event.fighter_a_stamina,
            'fighter_b_stamina': event.fighter_b_stamina,
            'fighter_a_head_damage': event.fighter_a_head_damage,
            'fighter_a_body_damage': event.fighter_a_body_damage,
            'fighter_a_leg_damage': event.fighter_a_leg_damage,
            'fighter_b_head_damage': event.fighter_b_head_damage,
            'fighter_b_body_damage': event.fighter_b_body_damage,
            'fighter_b_leg_damage': event.fighter_b_leg_damage,
            # NEW in v0.2.6: Position data
            'fighter_a_pos_x': event.fighter_a_pos_x,
            'fighter_a_pos_z': event.fighter_a_pos_z,
            'fighter_b_pos_x': event.fighter_b_pos_x,
            'fighter_b_pos_z': event.fighter_b_pos_z,
        })
    elif isinstance(event, RoundEndEvent):
        result.update({
            'fighter_a_score': event.fighter_a_score,
            'fighter_b_score': event.fighter_b_score,
            'winner_name': event.winner_name,
        })
    elif isinstance(event, MatchStartEvent):
        result.update({
            'fighter_a_name': event.fighter_a_name,
            'fighter_b_name': event.fighter_b_name,
        })
    elif isinstance(event, MatchEndEvent):
        result.update({
            'winner_name': event.winner_name,
            'method': event.method,
            'fighter_a_total_score': event.fighter_a_total_score,
            'fighter_b_total_score': event.fighter_b_total_score,
        })
    elif isinstance(event, CommentaryEvent):
        result.update({
            'text': event.text,
            'speaker': event.speaker,
        })
    
    # Include any metadata
    if event.metadata:
        result['metadata'] = event.metadata
    
    return result
