# app.py
from flask import Flask, render_template, Response, jsonify
from fighter import Fighter
from simulator import MuayThaiSimulator
from display import WebDisplay
from trash_talk import TrashTalkSystem
import json
import time
import os
import sys

# Get the absolute, real path to the directory where this script is located
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Add BASE_DIR to Python path so imports work from anywhere
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Change working directory to script location
os.chdir(BASE_DIR)

app = Flask(__name__)

@app.route('/')
def index():
    """Main page with fight button"""
    return render_template('index.html')

@app.route('/api/fighters')
def get_fighters():
    """Return list of available fighters"""
    fighters = [
        {'id': 'fighter_001', 'name': 'Somchai Petchyindee'},
        {'id': 'fighter_002', 'name': 'Nong-O Gaiyanghadao'}
    ]
    return jsonify(fighters)

@app.route('/api/simulate/<fighter_a_id>/<fighter_b_id>')
def simulate_fight(fighter_a_id, fighter_b_id):
    """Stream fight simulation in real-time using SSE"""
    
    def generate():
        try:
            # Load fighters
            fighter_a = Fighter.from_json(f"data/fighters/{fighter_a_id}.json")
            fighter_b = Fighter.from_json(f"data/fighters/{fighter_b_id}.json")
            
            # Create simulator
            simulator = StreamingSimulator(fighter_a, fighter_b, real_time=False)
            
            # Stream the match
            for message in simulator.simulate_match_streaming():
                yield f"data: {message}\n\n"
                
        except FileNotFoundError as e:
            error_msg = json.dumps({
                'type': 'error',
                'message': f'Fighter not found: {str(e)}'
            })
            yield f"data: {error_msg}\n\n"
            
        except Exception as e:
            error_msg = json.dumps({
                'type': 'error',
                'message': f'Simulation error: {str(e)}'
            })
            yield f"data: {error_msg}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')

class StreamingSimulator(MuayThaiSimulator):
    """Modified simulator that yields HTML frames for web streaming"""
    
    def __init__(self, fighter_a, fighter_b, real_time=False):
        super().__init__(fighter_a, fighter_b, real_time)
        self.web_display = WebDisplay(fighter_a.name, fighter_b.name)
        self.trash_talk = TrashTalkSystem(fighter_a, fighter_b)
    
    def simulate_match_streaming(self):
        """Generator that yields HTML frames"""
        
        # Send initial setup message
        yield json.dumps({
            'type': 'setup',
            'css': self.web_display.get_css()
        })
        
        # Generate and send weigh-in trash talk
        weigh_in = self.trash_talk.generate_weigh_in()
        yield json.dumps({
            'type': 'weigh_in',
            'fighter_a_name': self.fighter_a.name,
            'fighter_b_name': self.fighter_b.name,
            'fighter_a_quote': weigh_in['fighter_a'],
            'fighter_b_quote': weigh_in['fighter_b']
        })
        
        # Small delay to let user read the trash talk
        time.sleep(3)
        
        rounds = []
        
        for round_num in range(1, 6):
            # Simulate round and yield HTML frames
            for frame_data in self.simulate_round_streaming(round_num):
                yield frame_data
                
            round_result = self.get_last_round_result()
            round_result.round_num = round_num
            rounds.append(round_result)
            
            # Check for finish
            if self.fighter_a_health < 20:
                yield json.dumps({
                    'type': 'finish',
                    'winner': self.fighter_b.name,
                    'method': f"TKO Round {round_num}"
                })
                return
            elif self.fighter_b_health < 20:
                yield json.dumps({
                    'type': 'finish',
                    'winner': self.fighter_a.name,
                    'method': f"TKO Round {round_num}"
                })
                return
            
            # Break between rounds
            if round_num < 5:
                break_time = 2
                yield json.dumps({
                    'type': 'break',
                    'text': f"{break_time} second break..."
                })
                
                # Send keepalive pings during break to prevent timeout
                for _ in range(break_time):
                    time.sleep(1)
                    yield json.dumps({'type': 'keepalive'})
        
        # Final decision
        a_total = sum(r.fighter_a_score for r in rounds)
        b_total = sum(r.fighter_b_score for r in rounds)
        
        if a_total > b_total:
            winner = self.fighter_a.name
            method = f"Decision ({a_total}-{b_total})"
        elif b_total > a_total:
            winner = self.fighter_b.name
            method = f"Decision ({b_total}-{a_total})"
        else:
            winner = "Draw"
            method = f"Draw ({a_total}-{a_total})"
        
        yield json.dumps({
            'type': 'finish',
            'winner': winner,
            'method': method
        })
    
    def simulate_round_streaming(self, round_num):
        """Generator that yields HTML frames for each exchange"""
        num_exchanges = 12
        
        round_duration = 15 if not self.real_time else 180
        time_per_exchange = round_duration / num_exchanges
        
        a_round_damage = 0.0
        b_round_damage = 0.0
        
        for i in range(num_exchanges):
            time_remaining = round_duration - (i * time_per_exchange)
            time_str = self.format_time(int(time_remaining))
            
            desc, a_dmg, b_dmg, a_stam, b_stam = self.simulate_exchange(round_num)
            
            # Apply effects
            self.fighter_a_health -= a_dmg
            self.fighter_b_health -= b_dmg
            
            cardio_factor_a = self.fighter_a.stats.cardio / 100.0
            cardio_factor_b = self.fighter_b.stats.cardio / 100.0
            
            self.fighter_a_stamina -= a_stam * (1.0 - cardio_factor_a * 0.3)
            self.fighter_b_stamina -= b_stam * (1.0 - cardio_factor_b * 0.3)
            
            self.fighter_a_stamina = max(20, self.fighter_a_stamina)
            self.fighter_b_stamina = max(20, self.fighter_b_stamina)
            
            a_round_damage += a_dmg
            b_round_damage += b_dmg
            
            # Determine actions for visual
            fighter_a_action = self._get_action_type(desc, self.fighter_a.name)
            fighter_b_action = self._get_action_type(desc, self.fighter_b.name)
            
            # Calculate current round score for display
            if b_round_damage > a_round_damage * 1.3:
                a_score, b_score = 10, 9
            elif a_round_damage > b_round_damage * 1.3:
                a_score, b_score = 9, 10
            elif b_round_damage > a_round_damage:
                a_score, b_score = 10, 9
            elif a_round_damage > b_round_damage:
                a_score, b_score = 9, 10
            else:
                a_score, b_score = 10, 10
            
            # Create state for rendering
            state = {
                'round_num': round_num,
                'time_remaining': time_str,
                'fighter_a_health': self.fighter_a_health,
                'fighter_b_health': self.fighter_b_health,
                'fighter_a_stamina': self.fighter_a_stamina,
                'fighter_b_stamina': self.fighter_b_stamina,
                'action': desc,
                'fighter_a_action': fighter_a_action,
                'fighter_b_action': fighter_b_action,
                'fighter_a_score': a_score,
                'fighter_b_score': b_score,
            }
            
            # Render HTML frame
            html = self.web_display.render_frame_html(state)
            
            yield json.dumps({
                'type': 'frame',
                'html': html
            })
            
            time.sleep(time_per_exchange)
        
        # Score the round for tracking
        if b_round_damage > a_round_damage * 1.3:
            self.last_round_score = (10, 9, self.fighter_a.name)
        elif a_round_damage > b_round_damage * 1.3:
            self.last_round_score = (9, 10, self.fighter_b.name)
        elif b_round_damage > a_round_damage:
            self.last_round_score = (10, 9, self.fighter_a.name)
        elif a_round_damage > b_round_damage:
            self.last_round_score = (9, 10, self.fighter_b.name)
        else:
            self.last_round_score = (10, 10, "Draw")
        
        # Recover stamina
        self.fighter_a_stamina = min(100, self.fighter_a_stamina + 15)
        self.fighter_b_stamina = min(100, self.fighter_b_stamina + 15)
    
    def get_last_round_result(self):
        """Return RoundResult for the last simulated round"""
        from simulator import RoundResult
        a_score, b_score, winner = self.last_round_score
        return RoundResult(
            round_num=0,
            fighter_a_score=a_score,
            fighter_b_score=b_score,
            fighter_a_damage_dealt=0,
            fighter_b_damage_dealt=0,
            fighter_a_stamina_used=0,
            fighter_b_stamina_used=0,
            exchanges=[],
            winner=winner
        )


if __name__ == '__main__':
    # Check if script was run with relative path (contains ..)
    # Flask's reloader has issues with relative paths
    script_path = sys.argv[0]
    use_debug = '..' not in script_path and not script_path.startswith('.')
    
    if not use_debug:
        print("Note: Debug mode disabled because script was run with relative path.")
        print("For debug mode, run from the app directory or use absolute path.")
    
    app.run(debug=use_debug, port=5001, host='127.0.0.1')