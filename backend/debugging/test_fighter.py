# test_fighter.py
from fighter import Fighter, PhysicalAttributes, TrainingProfile

def create_test_fighters():
    """Create two test fighters with different profiles"""
    
    # Fighter 1: Power-focused brawler
    print("Creating Fighter 1: Somchai (Power Brawler)")
    physical1 = PhysicalAttributes(
        height_cm=175,
        weight_kg=70,
        age=25,
        muscle_mass_percent=75,  # High muscle = more power, less cardio
        fast_twitch_ratio=60     # Decent speed
    )
    
    training1 = TrainingProfile(
        striking_hours=800,
        clinch_hours=500,
        cardio_hours=400,        # Lower cardio training
        sparring_hours=600
    )
    
    fighter1 = Fighter(
        fighter_id="fighter_001",
        name="Somchai Petchyindee",
        discipline="Muay Thai",
        physical=physical1,
        training=training1
    )
    
    fighter1.display_stats()
    fighter1.to_json("data/fighters/somchai.json")
    print("Saved to data/fighters/somchai.json\n")
    
    # Fighter 2: Speed and cardio specialist
    print("Creating Fighter 2: Nong-O (Speed & Cardio)")
    physical2 = PhysicalAttributes(
        height_cm=178,
        weight_kg=70,
        age=28,
        muscle_mass_percent=65,  # Lower muscle = better cardio
        fast_twitch_ratio=75     # High fast-twitch = more speed
    )
    
    training2 = TrainingProfile(
        striking_hours=700,
        clinch_hours=300,
        cardio_hours=800,        # High cardio training
        sparring_hours=700
    )
    
    fighter2 = Fighter(
        fighter_id="fighter_002",
        name="Nong-O Gaiyanghadao",
        discipline="Muay Thai",
        physical=physical2,
        training=training2
    )
    
    fighter2.display_stats()
    fighter2.to_json("data/fighters/nongo.json")
    print("Saved to data/fighters/nongo.json\n")
    
    return fighter1, fighter2

if __name__ == "__main__":
    print("=" * 60)
    print("Combat Protocol - Fighter Creation Test")
    print("=" * 60)
    
    fighter1, fighter2 = create_test_fighters()
    
    print("\n" + "=" * 60)
    print("Summary:")
    print("{}: Power={:.1f}, Speed={:.1f}, Cardio={:.1f}".format(
        fighter1.name, fighter1.stats.power, fighter1.stats.speed, fighter1.stats.cardio))
    print("{}: Power={:.1f}, Speed={:.1f}, Cardio={:.1f}".format(
        fighter2.name, fighter2.stats.power, fighter2.stats.speed, fighter2.stats.cardio))
    print("=" * 60)