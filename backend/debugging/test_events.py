#!/usr/bin/env python3
# test_events.py
"""
Test the new event-based simulator and renderer.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fighter import Fighter
from simulator_v2 import MuayThaiSimulatorV2
from renderer_2d import Renderer2D
from events import EventType, event_to_dict
import json


def test_event_flow():
    """Test that simulator generates events and renderer handles them"""
    print("Loading fighters...")
    fighter_a = Fighter.from_json("data/fighters/somchai.json")
    fighter_b = Fighter.from_json("data/fighters/nongo.json")
    
    print(f"Fighter A: {fighter_a.name}")
    print(f"Fighter B: {fighter_b.name}")
    print()
    
    # Create simulator and renderer
    simulator = MuayThaiSimulatorV2(fighter_a, fighter_b, real_time=False)
    renderer = Renderer2D()
    renderer.init(fighter_a.name, fighter_b.name)
    
    print("Simulating match...")
    print("=" * 60)
    
    event_counts = {}
    
    # Run simulation
    match_gen = simulator.simulate_match_streaming()
    
    try:
        while True:
            event = next(match_gen)
            
            # Count event types
            event_type = event.event_type.name
            event_counts[event_type] = event_counts.get(event_type, 0) + 1
            
            # Pass to renderer
            renderer.handle_event(event)
            
            # Print significant events
            if event.event_type == EventType.MATCH_START:
                print(f"MATCH START: {event.fighter_a_name} vs {event.fighter_b_name}")
            elif event.event_type == EventType.ROUND_START:
                print(f"\n--- ROUND {event.round_num} ---")
            elif event.event_type == EventType.STRIKE:
                if event.damage > 0:
                    print(f"  {event.attacker.name} -> {event.move.name}: {event.result.name} ({event.damage:.1f} dmg)")
            elif event.event_type == EventType.CLINCH:
                if event.damage > 0:
                    print(f"  CLINCH: {event.initiator.name} {event.move.name} ({event.damage:.1f} dmg)")
            elif event.event_type == EventType.KNOCKDOWN:
                print(f"  *** KNOCKDOWN: Fighter {event.fighter.name} is DOWN! ***")
            elif event.event_type == EventType.ROUND_END:
                print(f"  Round {event.round_num} ends: {event.fighter_a_score}-{event.fighter_b_score} ({event.winner_name})")
            elif event.event_type == EventType.MATCH_END:
                print(f"\n{'=' * 60}")
                print(f"WINNER: {event.winner_name}")
                print(f"Method: {event.method}")
            elif event.event_type == EventType.BREAK_START:
                print(f"  [Break: {event.duration_seconds}s]")
            
            # Render frame (just to test it doesn't crash)
            frame = renderer.render(0.1)
            
    except StopIteration as e:
        result = e.value
        print(f"\nMatch complete!")
    
    print("\n" + "=" * 60)
    print("Event counts:")
    for event_type, count in sorted(event_counts.items()):
        print(f"  {event_type}: {count}")
    
    print("\n" + "=" * 60)
    print("Final renderer state:")
    final_frame = renderer.render(0)
    print(f"  Fighter A ({final_frame['fighter_a']['name']}):")
    print(f"    Health: {final_frame['fighter_a']['health']:.1f}")
    print(f"    Stamina: {final_frame['fighter_a']['stamina']:.1f}")
    print(f"    Pose: {final_frame['fighter_a']['pose']}")
    print(f"  Fighter B ({final_frame['fighter_b']['name']}):")
    print(f"    Health: {final_frame['fighter_b']['health']:.1f}")
    print(f"    Stamina: {final_frame['fighter_b']['stamina']:.1f}")
    print(f"    Pose: {final_frame['fighter_b']['pose']}")
    
    print("\nTest passed!")


def test_event_serialization():
    """Test that events can be serialized to JSON"""
    print("\nTesting event serialization...")
    
    fighter_a = Fighter.from_json("data/fighters/somchai.json")
    fighter_b = Fighter.from_json("data/fighters/nongo.json")
    
    simulator = MuayThaiSimulatorV2(fighter_a, fighter_b, real_time=False)
    
    # Just test first few events
    match_gen = simulator.simulate_match_streaming()
    
    for i, event in enumerate(match_gen):
        if i >= 10:
            break
        
        # Convert to dict
        event_dict = event_to_dict(event)
        
        # Serialize to JSON
        json_str = json.dumps(event_dict)
        
        # Parse back
        parsed = json.loads(json_str)
        
        print(f"  Event {i}: {parsed['event_type']}")
    
    print("Serialization test passed!")


if __name__ == '__main__':
    test_event_flow()
    test_event_serialization()
