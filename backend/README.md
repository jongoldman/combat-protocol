# Combat Protocol - Visual Fight Simulator

Physics-based fighting simulation platform with real-time visual displays.

## Features

- **Terminal Display**: Animated ASCII fights in your terminal with colored health/stamina bars
- **Web Display**: Browser-based fights with smooth HTML/CSS animations
- **Physics Engine**: Realistic combat simulation based on fighter attributes and training
- **Real-time Updates**: Watch fights unfold action-by-action

## Quick Start

### Terminal Version (Recommended for Local Testing)

Run fights directly in your Mac terminal:

```bash
python3 run_terminal_fight.py
```

This will:
1. Load two demo fighters (or create them if files don't exist)
2. Ask if you want fast-forward (15 sec/round) or real-time (3 min/round)
3. Display the fight with:
   - Colored health and stamina bars
   - Fighter avatars (emojis)
   - Real-time action descriptions
   - Round scores

**Controls:**
- The display updates automatically each exchange
- Screen clears between updates for smooth animation
- Works best in a full-screen terminal window

### Web Version

Start the Flask server:

```bash
python3 app.py
```

Then open your browser to:
```
http://127.0.0.1:5001
```

Click "Start Fight" to watch the fight with:
- Animated health/stamina bars
- Visual fighter representations
- Real-time action text
- Final results overlay

## File Structure

```
combat-protocol/
├── fighter.py          # Fighter class with physics-based stats
├── simulator.py        # Match simulation engine  
├── display.py          # Visual display system (terminal + web)
├── app.py             # Flask web server
├── run_terminal_fight.py  # Terminal viewer script
├── data/
│   └── fighters/      # Fighter JSON files
├── templates/
│   └── index.html     # Web interface
└── requirements.txt   # Python dependencies
```

## How It Works

### Fighter Stats
Fighters have measurable **physical attributes**:
- Height, weight, age
- Muscle mass percentage
- Fast-twitch muscle ratio

And **training profiles**:
- Striking, clinch, cardio, sparring hours

These derive **combat stats**:
- Power, speed, cardio, chin
- Technique, clinch, defense, fight IQ

### Match Simulation
- 5 rounds, 3 minutes each (180 seconds)
- 12-15 exchanges per round
- Each exchange: striking, clinch, or defensive
- Health and stamina tracked in real-time
- 10-point must scoring system
- TKO if health drops below 20%

### Display System
The `display.py` module provides two renderers:

**TerminalDisplay**: 
- ANSI colors for health status (green > yellow > red)
- Unicode characters for progress bars
- Emoji fighters with action states
- Screen clearing for smooth updates

**WebDisplay**:
- HTML/CSS rendering
- Smooth bar animations
- Dynamic fighter avatars
- JSON streaming via Server-Sent Events

## Customization

### Speed Settings
Fast-forward mode (15 sec/round) vs real-time (3 min/round):

```python
simulator = MuayThaiSimulator(fighter_a, fighter_b, real_time=False)  # Fast
simulator = MuayThaiSimulator(fighter_a, fighter_b, real_time=True)   # Real-time
```

### Creating Fighters

```python
from fighter import Fighter, PhysicalAttributes, TrainingProfile

my_fighter = Fighter(
    fighter_id='custom_001',
    name='Your Fighter Name',
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

# Save to JSON
my_fighter.to_json('data/fighters/my_fighter.json')
```

### Visual Customization

The display is intentionally simple (ASCII/Unicode + basic emojis) to make it easy to swap out later for:
- 2D sprite animations
- 3D models
- More sophisticated graphics

All visual logic is isolated in `display.py`, so you can replace it without touching the simulation engine.

## Dependencies

```bash
pip install -r requirements.txt
```

Core dependencies:
- Flask (web server)
- Standard library (json, time, random, dataclasses)

## Next Steps

Ideas for expansion:
- Fighter roster management
- Match history tracking
- Multiple fighting disciplines
- Advanced combat mechanics (submissions, special moves)
- Tournament brackets
- Fighter training progression
- Betting/prediction system

## Notes

- Terminal colors require ANSI support (works on Mac/Linux, may need Windows Terminal on Windows)
- Emoji display depends on your terminal's font support
- Web version tested in Chrome/Firefox/Safari
- Fast-forward mode recommended for development/testing
