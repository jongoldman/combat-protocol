# test_match.py
from fighter import Fighter
from simulator import MuayThaiSimulator

# Load the two fighters we created
fighter_a = Fighter.from_json("data/fighters/somchai.json")
fighter_b = Fighter.from_json("data/fighters/nongo.json")

# Display fighters
print("\n" + "="*60)
print("FIGHTER PROFILES")
print("="*60)
fighter_a.display_stats()
fighter_b.display_stats()

# Simulate the match with real-time output
# real_time=False means fast-forward (15 sec per round)
# real_time=True means actual 3 minute rounds
###simulator = MuayThaiSimulator(fighter_a, fighter_b, real_time=False)
simulator = MuayThaiSimulator(fighter_a, fighter_b, real_time=True)
result = simulator.simulate_match(verbose=True)

print("\n" + "="*60)
print("MATCH SUMMARY")
print("="*60)
print(f"Winner: {result.winner}")
print(f"Method: {result.method}")
print(f"Total Rounds: {len(result.rounds)}")
