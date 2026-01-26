#!/usr/bin/env python3
"""
Terminal fight viewer for Combat Protocol
Run this to watch fights in your terminal
"""

from fighter import Fighter, PhysicalAttributes, TrainingProfile
from simulator import MuayThaiSimulator

def main():
    print("\n" + "="*70)
    print("COMBAT PROTOCOL - Terminal Viewer")
    print("="*70)
    print()
    
    # Load fighters
    try:
        fighter_a = Fighter.from_json('data/fighters/somchai.json')
        fighter_b = Fighter.from_json('data/fighters/nongo.json')
    except FileNotFoundError:
        print("Creating demo fighters...")
        
        # Create demo fighters if files don't exist
        fighter_a = Fighter(
            fighter_id='demo_001',
            name='Somchai Petchyindee',
            discipline='Muay Thai',
            physical=PhysicalAttributes(
                height_cm=175,
                weight_kg=70,
                age=25,
                muscle_mass_percent=75,
                fast_twitch_ratio=60
            ),
            training=TrainingProfile(
                striking_hours=800,
                clinch_hours=500,
                cardio_hours=400,
                sparring_hours=600
            )
        )
        
        fighter_b = Fighter(
            fighter_id='demo_002',
            name='Nong-O Gaiyanghadao',
            discipline='Muay Thai',
            physical=PhysicalAttributes(
                height_cm=172,
                weight_kg=68,
                age=28,
                muscle_mass_percent=70,
                fast_twitch_ratio=55
            ),
            training=TrainingProfile(
                striking_hours=900,
                clinch_hours=600,
                cardio_hours=500,
                sparring_hours=700
            )
        )
    
    print(f"Loading: {fighter_a.name} vs {fighter_b.name}")
    print()
    
    # Ask for speed
    print("Select speed:")
    print("  1. Fast-forward (15 seconds per round)")
    print("  2. Real-time (3 minutes per round)")
    choice = input("\nChoice (1 or 2): ").strip()
    
    real_time = (choice == '2')
    
    # Create simulator
    simulator = MuayThaiSimulator(fighter_a, fighter_b, real_time=real_time)
    
    # Run the match
    result = simulator.simulate_match(verbose=True)
    
    print("\nFight complete!")
    print(f"Winner: {result.winner}")
    print(f"Method: {result.method}")
    print()

if __name__ == '__main__':
    main()
