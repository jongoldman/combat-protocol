# renderer.py
"""
Renderer interface for Combat Protocol.

This module defines the abstract Renderer interface that all visualization
backends must implement. This allows swapping between 2D sprites, 3D models,
terminal output, or any other visualization without changing simulation code.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from events import (
    FightEvent, EventType, FighterID,
    MatchStartEvent, RoundStartEvent, StrikeEvent, ClinchEvent,
    KnockdownEvent, StateUpdateEvent, RoundEndEvent, MatchEndEvent,
    CommentaryEvent, BreakStartEvent
)


@dataclass
class FighterVisualState:
    """
    Current visual state of a fighter.
    Renderers update this based on events and use it for drawing.
    """
    fighter_id: FighterID
    name: str
    
    # Current pose/animation
    pose: str = "idle"  # idle, jab, cross, kick, block, hurt, knockdown, etc.
    pose_start_time: float = 0.0
    pose_duration: float = 0.5  # How long the pose lasts before returning to idle
    
    # Position (normalized 0-1, renderer maps to actual coordinates)
    x: float = 0.0  # 0 = left edge, 1 = right edge
    y: float = 0.0  # 0 = ground, 1 = top
    
    # Stats for display
    health: float = 100.0
    stamina: float = 100.0
    
    # Damage indicators (for visual effects like bruising, limping)
    head_damage: float = 0.0
    body_damage: float = 0.0
    leg_damage: float = 0.0
    
    # State flags
    is_attacking: bool = False
    is_defending: bool = False
    is_hurt: bool = False
    is_down: bool = False
    in_clinch: bool = False


@dataclass
class FightVisualState:
    """Complete visual state of the fight"""
    fighter_a: FighterVisualState
    fighter_b: FighterVisualState
    
    round_num: int = 1
    time_remaining: float = 180.0  # Seconds remaining in round
    
    # Scores
    fighter_a_round_score: int = 10
    fighter_b_round_score: int = 10
    fighter_a_total_score: int = 0
    fighter_b_total_score: int = 0
    
    # Fight state
    is_in_clinch: bool = False
    is_paused: bool = False
    
    # Last action description (for text display)
    last_action: str = ""
    
    # Commentary queue
    commentary: List[str] = None
    
    def __post_init__(self):
        if self.commentary is None:
            self.commentary = []


class Renderer(ABC):
    """
    Abstract base class for fight renderers.
    
    Implementations:
    - Renderer2D: Canvas-based 2D sprite renderer (web)
    - Renderer3D: WebGL/Three.js 3D renderer (web, future)
    - TerminalRenderer: ASCII/Unicode terminal output
    
    The renderer maintains its own visual state and updates it based on
    events from the simulator. The simulator doesn't know or care how
    things are being visualized.
    """
    
    def __init__(self):
        self.state: Optional[FightVisualState] = None
        self.fighter_a_name: str = ""
        self.fighter_b_name: str = ""
    
    @abstractmethod
    def init(self, fighter_a_name: str, fighter_b_name: str, config: Dict[str, Any] = None) -> None:
        """
        Initialize the renderer with fighter info.
        
        Args:
            fighter_a_name: Display name for fighter A
            fighter_b_name: Display name for fighter B
            config: Optional renderer-specific configuration
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: FightEvent) -> None:
        """
        Process a fight event and update internal visual state.
        
        This is where the renderer interprets simulation events and
        decides how to visualize them. For example, a StrikeEvent
        might trigger a punch animation on the attacker and a hurt
        reaction on the defender.
        
        Args:
            event: The fight event to process
        """
        pass
    
    @abstractmethod
    def render(self, delta_time: float) -> Any:
        """
        Render the current frame.
        
        Args:
            delta_time: Seconds since last render call
            
        Returns:
            Renderer-specific output (HTML string, canvas commands, etc.)
        """
        pass
    
    @abstractmethod
    def destroy(self) -> None:
        """
        Clean up renderer resources.
        """
        pass
    
    def _init_visual_state(self, fighter_a_name: str, fighter_b_name: str) -> FightVisualState:
        """Helper to create initial visual state"""
        return FightVisualState(
            fighter_a=FighterVisualState(
                fighter_id=FighterID.A,
                name=fighter_a_name,
                x=0.25,  # Left side of arena
            ),
            fighter_b=FighterVisualState(
                fighter_id=FighterID.B,
                name=fighter_b_name,
                x=0.75,  # Right side of arena
            ),
        )
    
    def _get_fighter_state(self, fighter_id: FighterID) -> FighterVisualState:
        """Get visual state for a specific fighter"""
        if fighter_id == FighterID.A:
            return self.state.fighter_a
        return self.state.fighter_b
    
    def _map_move_to_pose(self, move_name: str) -> str:
        """
        Map a move type to a pose name.
        Override in subclass if you have different pose sets.
        """
        pose_map = {
            # Punches
            'JAB': 'jab',
            'CROSS': 'cross',
            'HOOK': 'hook',
            'UPPERCUT': 'uppercut',
            'BODY_PUNCH': 'body_punch',
            
            # Kicks
            'LEG_KICK': 'leg_kick',
            'BODY_KICK': 'body_kick',
            'HEAD_KICK': 'head_kick',
            
            # Clinch
            'KNEE': 'knee',
            'ELBOW': 'elbow',
            'CLINCH_ENTRY': 'clinch',
            'CLINCH_KNEE': 'knee',
            'CLINCH_ELBOW': 'elbow',
            'CLINCH_THROW': 'throw',
            
            # Defense
            'BLOCK': 'block',
            'SLIP': 'slip',
            'PARRY': 'parry',
            'CHECK': 'check',
        }
        return pose_map.get(move_name, 'idle')
    
    def _map_result_to_reaction(self, result_name: str) -> str:
        """Map a strike result to a defender reaction pose"""
        if result_name in ('LANDED_CLEAN', 'LANDED_PARTIAL'):
            return 'hurt'
        elif result_name in ('BLOCKED', 'CHECKED'):
            return 'block'
        elif result_name == 'MISSED':
            return 'idle'  # No reaction needed
        return 'idle'


class RendererFactory:
    """Factory for creating renderers by name"""
    
    _renderers: Dict[str, type] = {}
    
    @classmethod
    def register(cls, name: str, renderer_class: type) -> None:
        """Register a renderer class"""
        cls._renderers[name] = renderer_class
    
    @classmethod
    def create(cls, name: str) -> Renderer:
        """Create a renderer instance by name"""
        if name not in cls._renderers:
            raise ValueError(f"Unknown renderer: {name}. Available: {list(cls._renderers.keys())}")
        return cls._renderers[name]()
    
    @classmethod
    def available(cls) -> List[str]:
        """List available renderer names"""
        return list(cls._renderers.keys())
