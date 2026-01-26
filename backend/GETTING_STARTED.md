# Getting Started with Combat Protocol

## Installation & Setup

1. **Navigate to the project directory:**
```bash
cd combat-protocol
```

2. **Install dependencies:**
```bash
pip3 install -r requirements.txt
```

## Running Your First Fight

### Option 1: Terminal Mode (Easiest)

```bash
python3 run_terminal_fight.py
```

You'll see:
```
======================================================================
COMBAT PROTOCOL - Terminal Viewer
======================================================================

Loading: Somchai Petchyindee vs Nong-O Gaiyanghadao

Select speed:
  1. Fast-forward (15 seconds per round)
  2. Real-time (3 minutes per round)

Choice (1 or 2):
```

Choose option 1 for fast-forward mode. The terminal will update in real-time showing:

```
══════════════════════════════════════════════════════════════════════
  COMBAT PROTOCOL - ROUND 1 - TIME: 2:45
══════════════════════════════════════════════════════════════════════

       Somchai Petchyindee          VS       Nong-O Gaiyanghadao

  HP  ████████████████░░░░  85.5%       ██████████████████░░  92.3%

  STA ███████████████░░░░░  78.2%       ████████████████░░░░  81.5%

       👊                    😵

  ──────────────────────────────────────────────────────────────────────
  │              Somchai Petchyindee lands heavy strikes               │
  ──────────────────────────────────────────────────────────────────────

  Round Score: Somchai Petchyindee 10 - 9 Nong-O Gaiyanghadao
```

The display updates automatically every ~1 second (fast-forward mode).

### Option 2: Web Interface

1. **Start the Flask server:**
```bash
python3 app.py
```

2. **Open your browser to:**
```
http://127.0.0.1:5001
```

3. **Click "⚡ Start Fight ⚡"**

You'll see similar visuals but with:
- Smooth CSS animations
- Color-coded health bars
- Live updating stats
- Final result overlay

## Understanding the Display

### Terminal Display Elements

**Health Bars:**
- 🟢 Green: > 70% health (healthy)
- 🟡 Yellow: 40-70% health (hurt)  
- 🔴 Red: < 40% health (danger)

**Fighter Avatars:**
- 🧍 Idle stance
- 👊 Striking
- 🤼 Clinch fighting
- 🛡️ Defending
- 😵 Taking damage

**Action Box:**
Shows what's happening in the current exchange:
- "Fighter X lands heavy strikes"
- "Fighter X dominates the clinch"
- "Cautious exchange, both fighters reset"

**Round Score:**
Based on 10-point must system (winner gets 10, loser gets 9 or less)

## Creating Custom Fighters

### Method 1: Using Python

```python
from fighter import Fighter, PhysicalAttributes, TrainingProfile

# Define physical attributes
physical = PhysicalAttributes(
    height_cm=180,      # Height in centimeters
    weight_kg=75,       # Weight in kilograms
    age=26,            # Age affects chin durability
    muscle_mass_percent=80,  # 0-100, affects power vs cardio
    fast_twitch_ratio=70     # 0-100, affects speed vs endurance
)

# Define training background
training = TrainingProfile(
    striking_hours=1000,   # Total striking training
    clinch_hours=600,      # Clinch work
    cardio_hours=500,      # Cardio conditioning
    sparring_hours=800     # Sparring experience
)

# Create the fighter
my_fighter = Fighter(
    fighter_id='custom_001',
    name='Custom Fighter',
    discipline='Muay Thai',
    physical=physical,
    training=training
)

# View the derived stats
my_fighter.display_stats()

# Save to file
my_fighter.to_json('data/fighters/custom_001.json')
```

### Method 2: Edit JSON Directly

Create a file in `data/fighters/yourfighter.json`:

```json
{
  "id": "yourfighter",
  "name": "Your Fighter Name",
  "discipline": "Muay Thai",
  "physical": {
    "height_cm": 175,
    "weight_kg": 70,
    "age": 25,
    "muscle_mass_percent": 75,
    "fast_twitch_ratio": 60
  },
  "training": {
    "striking_hours": 800,
    "clinch_hours": 500,
    "cardio_hours": 400,
    "sparring_hours": 600
  }
}
```

Note: The `derived_stats` section is calculated automatically when you load the fighter.

## Running Custom Matchups

### In Terminal:

Modify `run_terminal_fight.py` to load your fighters:

```python
fighter_a = Fighter.from_json('data/fighters/yourfighter.json')
fighter_b = Fighter.from_json('data/fighters/somchai.json')
```

### In Web:

Modify the URL in `templates/index.html`:

```javascript
// Change this line:
eventSource = new EventSource('/api/simulate/somchai/nongo');

// To your fighters:
eventSource = new EventSource('/api/simulate/yourfighter/somchai');
```

## Performance Tips

### Fast Development Cycle:
```python
# Use fast-forward mode
sim = MuayThaiSimulator(fighter_a, fighter_b, real_time=False)
```

Each round takes ~15 seconds instead of 3 minutes.

### Testing Specific Scenarios:
```python
# Start with custom health/stamina
sim.fighter_a_health = 50.0
sim.fighter_b_stamina = 30.0

# Run a single round
result = sim.simulate_round(round_num=1, show_realtime=True)
```

## Understanding Fighter Stats

Stats are derived from physical attributes and training:

**Power** = f(weight, muscle_mass)
- Heavier fighters hit harder
- More muscle = more power

**Speed** = f(weight, fast_twitch_ratio)
- Lighter fighters are faster
- Higher fast-twitch ratio = quicker

**Cardio** = f(muscle_mass, fast_twitch_ratio, cardio_training)
- Less muscle mass = better endurance
- Lower fast-twitch = better stamina
- Cardio training improves it

**Chin** = f(age, weight)
- Younger fighters take hits better
- Heavier fighters are harder to hurt

**Technique** = f(striking_hours, fast_twitch)
- More training = better technique
- Fast-twitch helps technique precision

**Clinch** = f(clinch_hours)
- Direct correlation with clinch training

**Defense** = f(sparring_hours, speed)
- Experience improves defense
- Speed helps avoid strikes

**Fight IQ** = f(total_training, age)
- More total experience = better IQ
- Peak IQ around age 28-30

## Troubleshooting

**Terminal colors not showing:**
- Make sure your terminal supports ANSI colors
- On Mac: Use Terminal.app or iTerm2
- On Windows: Use Windows Terminal

**Emojis not displaying:**
- Update your terminal font
- Mac: SF Mono or Menlo work well
- Some fonts don't support all emojis

**Web server won't start:**
```bash
# Check if port 5001 is in use
lsof -i :5001

# Use a different port
python3 app.py  # then edit app.py to change port
```

**Fighter JSON won't load:**
- Check JSON syntax (use jsonlint.com)
- Verify all required fields are present
- Stats are auto-calculated, don't include them in JSON

## What's Next?

Now that you have the visual system working, you can:

1. **Add more fighters** - Create a diverse roster
2. **Build a tournament system** - Bracket-style competitions
3. **Track match history** - Save results to a database
4. **Add fighter progression** - Training improves stats over time
5. **Implement betting** - Prediction markets for fights
6. **New disciplines** - Boxing, MMA, Kickboxing with different mechanics

The display system is intentionally simple so you can easily replace it later with more sophisticated graphics without touching the simulation engine!
