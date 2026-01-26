# fighter.py
import json
from dataclasses import dataclass
from typing import Dict

@dataclass
class PhysicalAttributes:
    """Core physical attributes - measurable and verifiable"""
    height_cm: float
    weight_kg: float
    age: int
    muscle_mass_percent: float  # 0-100, affects power/cardio tradeoff
    fast_twitch_ratio: float    # 0-100, affects speed/endurance tradeoff

@dataclass
class TrainingProfile:
    """Cumulative training hours"""
    striking_hours: int
    clinch_hours: int
    cardio_hours: int
    sparring_hours: int

@dataclass
class FightingStyle:
    """Fighting style preferences and tendencies"""
    body_attack_preference: float  # 0-100, how often they target body vs head
    leg_kick_tendency: float       # 0-100, for Muay Thai leg kicks
    power_punch_frequency: float   # 0-100, how often they go for big shots
    
@dataclass
class Durability:
    """Resistance to different damage types"""
    head_durability: float         # 0-100, chin/ability to take head shots
    body_durability: float         # 0-100, ability to absorb body shots
    leg_durability: float          # 0-100, resistance to leg damage
    recovery_rate: float           # 0-100, how well they recover between rounds

@dataclass
class Personality:
    """Personality traits that drive trash talk and behavior"""
    trash_talk_frequency: float    # 0-100, how often they talk
    confidence: float               # 0-100, humble to cocky
    aggression: float               # 0-100, calm to angry
    respect: float                  # 0-100, disrespectful to respectful
    humor: float                    # 0-100, serious to joker
    verbosity: float                # 0-100, one-liners to speeches

@dataclass
class FighterStats:
    """Derived combat statistics"""
    power: float
    speed: float
    cardio: float
    chin: float
    technique: float
    clinch: float
    defense: float
    fight_iq: float

class Fighter:
    def __init__(self, fighter_id: str, name: str, discipline: str,
                 physical: PhysicalAttributes, training: TrainingProfile,
                 style: FightingStyle = None, durability: Durability = None,
                 personality: Personality = None):
        self.id = fighter_id
        self.name = name
        self.discipline = discipline
        self.physical = physical
        self.training = training
        
        # Set defaults if not provided
        self.style = style or FightingStyle(
            body_attack_preference=30.0,
            leg_kick_tendency=20.0,
            power_punch_frequency=40.0
        )
        self.durability = durability or Durability(
            head_durability=70.0,
            body_durability=70.0,
            leg_durability=70.0,
            recovery_rate=60.0
        )
        self.personality = personality or Personality(
            trash_talk_frequency=50.0,
            confidence=60.0,
            aggression=50.0,
            respect=60.0,
            humor=40.0,
            verbosity=50.0
        )
        
        self.stats = self._derive_stats()

    def _derive_stats(self) -> FighterStats:
        """
        Derive combat stats from physical attributes and training.
        All stats normalized to 0-100 scale.
        Designed so elite fighters reach 75-85 in specialties, not 100.
        """
        p = self.physical
        t = self.training
        
        # Power: weight + muscle mass (further scaled down)
        power = (p.weight_kg * 0.25) + (p.muscle_mass_percent * 0.25)
        power = min(100, power)
        
        # Speed: inversely related to weight, boosted by fast-twitch (capped lower)
        speed = 40 + (100 - p.weight_kg) * 0.2 + (p.fast_twitch_ratio * 0.25)
        speed = max(0, min(100, speed))
        
        # Cardio: inversely related to muscle mass, boosted by training (scaled even more)
        base_cardio = 30 + (100 - p.muscle_mass_percent) * 0.25 + ((100 - p.fast_twitch_ratio) * 0.12)
        cardio = base_cardio + (t.cardio_hours / 40)  # Training has less impact
        cardio = min(100, cardio)        
        
        # Chin: degrades with age, improves with weight (capped lower)
        chin = 40 + (100 - (p.age - 18) * 1.2) * 0.3 + (p.weight_kg * 0.12)
        chin = max(0, min(100, chin))
        
        # Technique: from striking training (scaled appropriately)
        technique = (t.striking_hours / 20) * (1 + p.fast_twitch_ratio / 400)
        technique = min(100, technique)
        
        # Clinch: from clinch training
        clinch = t.clinch_hours / 10
        clinch = min(100, clinch)
        
        # Defense: sparring experience + speed component
        defense = (t.sparring_hours / 15) + (speed * 0.1)
        defense = min(100, defense)
        
        # Fight IQ: total experience with age wisdom bonus
        total_hours = t.striking_hours + t.clinch_hours + t.cardio_hours + t.sparring_hours
        fight_iq = (total_hours / 50) + max(0, (30 - p.age) * 0.5)
        fight_iq = min(100, max(0, fight_iq))
        
        return FighterStats(
            power=round(power, 1),
            speed=round(speed, 1),
            cardio=round(cardio, 1),
            chin=round(chin, 1),
            technique=round(technique, 1),
            clinch=round(clinch, 1),
            defense=round(defense, 1),
            fight_iq=round(fight_iq, 1)
        )

            
    @classmethod
    def from_json(cls, filepath: str):
        """Load fighter from JSON file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        physical = PhysicalAttributes(**data['physical'])
        training = TrainingProfile(**data['training'])
        
        # Optional: load style, durability, and personality if present
        style = FightingStyle(**data['style']) if 'style' in data else None
        durability = Durability(**data['durability']) if 'durability' in data else None
        personality = Personality(**data['personality']) if 'personality' in data else None
        
        return cls(data['id'], data['name'], data['discipline'], physical, training, 
                   style, durability, personality)
    
    def to_json(self, filepath: str):
        """Save fighter to JSON file"""
        data = {
            'id': self.id,
            'name': self.name,
            'discipline': self.discipline,
            'physical': {
                'height_cm': self.physical.height_cm,
                'weight_kg': self.physical.weight_kg,
                'age': self.physical.age,
                'muscle_mass_percent': self.physical.muscle_mass_percent,
                'fast_twitch_ratio': self.physical.fast_twitch_ratio
            },
            'training': {
                'striking_hours': self.training.striking_hours,
                'clinch_hours': self.training.clinch_hours,
                'cardio_hours': self.training.cardio_hours,
                'sparring_hours': self.training.sparring_hours
            },
            'style': {
                'body_attack_preference': self.style.body_attack_preference,
                'leg_kick_tendency': self.style.leg_kick_tendency,
                'power_punch_frequency': self.style.power_punch_frequency
            },
            'durability': {
                'head_durability': self.durability.head_durability,
                'body_durability': self.durability.body_durability,
                'leg_durability': self.durability.leg_durability,
                'recovery_rate': self.durability.recovery_rate
            },
            'personality': {
                'trash_talk_frequency': self.personality.trash_talk_frequency,
                'confidence': self.personality.confidence,
                'aggression': self.personality.aggression,
                'respect': self.personality.respect,
                'humor': self.personality.humor,
                'verbosity': self.personality.verbosity
            },
            'derived_stats': {
                'power': self.stats.power,
                'speed': self.stats.speed,
                'cardio': self.stats.cardio,
                'chin': self.stats.chin,
                'technique': self.stats.technique,
                'clinch': self.stats.clinch,
                'defense': self.stats.defense,
                'fight_iq': self.stats.fight_iq
            }
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
    
    def display_stats(self):
        """Pretty print fighter info"""
        print(f"\n{'='*50}")
        print(f"Fighter: {self.name}")
        print(f"ID: {self.id} | Discipline: {self.discipline}")
        print(f"{'='*50}")
        print(f"\nPhysical Attributes:")
        print(f"  Height: {self.physical.height_cm} cm")
        print(f"  Weight: {self.physical.weight_kg} kg")
        print(f"  Age: {self.physical.age}")
        print(f"  Muscle Mass: {self.physical.muscle_mass_percent}%")
        print(f"  Fast-Twitch Ratio: {self.physical.fast_twitch_ratio}%")
        print(f"\nTraining Profile:")
        print(f"  Striking: {self.training.striking_hours} hours")
        print(f"  Clinch: {self.training.clinch_hours} hours")
        print(f"  Cardio: {self.training.cardio_hours} hours")
        print(f"  Sparring: {self.training.sparring_hours} hours")
        print(f"\nDerived Stats:")
        print(f"  Power:     {self.stats.power:>5.1f}")
        print(f"  Speed:     {self.stats.speed:>5.1f}")
        print(f"  Cardio:    {self.stats.cardio:>5.1f}")
        print(f"  Chin:      {self.stats.chin:>5.1f}")
        print(f"  Technique: {self.stats.technique:>5.1f}")
        print(f"  Clinch:    {self.stats.clinch:>5.1f}")
        print(f"  Defense:   {self.stats.defense:>5.1f}")
        print(f"  Fight IQ:  {self.stats.fight_iq:>5.1f}")
        print(f"{'='*50}\n")
