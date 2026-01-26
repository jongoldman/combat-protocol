# app_v2.py
"""
Flask web server for Combat Protocol using event-based architecture.

This version uses the new simulator_v2 and renderer system for
clean separation between simulation and visualization.

NOW WITH LOGIN PROTECTION
"""

from dotenv import load_dotenv
import os

# Get the directory where this script is located
BASE_DIR = os.path.dirname(os.path.realpath(__file__))
# Load .env file from the same directory as this script
dotenv_path = os.path.join(BASE_DIR, '.env')
load_dotenv(dotenv_path)

from flask import Flask, render_template, Response, jsonify, request, redirect, session, render_template_string, send_from_directory
from functools import wraps
from fighter import Fighter
from simulator_v2 import MuayThaiSimulatorV2
from renderer_2d import Renderer2D
from events import event_to_dict, EventType
from trash_talk import TrashTalkSystem
from fighter_generator import FighterGenerator
import json
import time
import os
import sys
from flask_cors import CORS

# VERSION TRACKING
APP_VERSION = "v0.2.9"  # Capsule-based collision detection (Level 2)

def print_version_banner():
    """Print a big ASCII banner with the version"""
    banner = f"""
╔══════════════════════════════════════════════════════════╗
║                                                          ║
║              COMBAT PROTOCOL BACKEND                     ║
║                                                          ║
║                   VERSION: {APP_VERSION}                        ║
                    (FIST-BUMP INTRO SEQUENCE
║                   (WITH IMPROVED COLLISION DETECTION)    ║
║                   (MODELS API ADDED)                     ║
║                                                          ║
╚══════════════════════════════════════════════════════════╝
"""
    print(banner)

# Get the absolute, real path to the directory where this script is located
BASE_DIR = os.path.dirname(os.path.realpath(__file__))

# Add BASE_DIR to Python path so imports work from anywhere
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

# Change working directory to script location
os.chdir(BASE_DIR)

app = Flask(__name__)

# After: app = Flask(__name__)
# Add:
##CORS(app)
CORS(app, supports_credentials=True, origins=["http://localhost:5173"])

# TBD: Disable caching for development
@app.after_request
def add_header(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '-1'
    return response

# Security configuration
app.secret_key = os.environ.get('SECRET_KEY', 'change-this-in-production-please')
SITE_PASSWORD = os.environ.get('SITE_PASSWORD', 'fubar')

# Login protection decorator
def login_required(f):
    """Decorator to require authentication for routes"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get('authenticated'):
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function


# LOGIN PAGE TEMPLATE
LOGIN_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Combat Protocol - Login</title>
    <meta name="robots" content="noindex, nofollow">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            background: linear-gradient(135deg, #0f0f0f 0%, #1a1a1a 100%);
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            color: #fff;
        }
        
        .login-container {
            background: rgba(30, 30, 30, 0.9);
            padding: 50px 40px;
            border-radius: 16px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
            text-align: center;
            max-width: 400px;
            width: 90%;
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        h1 {
            font-size: 2rem;
            margin-bottom: 10px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
            letter-spacing: 1px;
        }
        
        .subtitle {
            color: #888;
            font-size: 0.9rem;
            margin-bottom: 40px;
            letter-spacing: 2px;
            text-transform: uppercase;
        }
        
        form {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        
        input[type="password"] {
            padding: 15px 20px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.05);
            color: #fff;
            font-size: 1rem;
            transition: all 0.3s ease;
        }
        
        input[type="password"]:focus {
            outline: none;
            border-color: #ff6b6b;
            background: rgba(255, 255, 255, 0.08);
        }
        
        input[type="password"]::placeholder {
            color: #666;
        }
        
        button {
            padding: 15px 30px;
            background: linear-gradient(135deg, #ff6b6b, #ee5a6f);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);
        }
        
        button:active {
            transform: translateY(0);
        }
        
        .error {
            color: #ff6b6b;
            padding: 10px;
            border-radius: 6px;
            background: rgba(255, 107, 107, 0.1);
            border: 1px solid rgba(255, 107, 107, 0.3);
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>⚔️ COMBAT PROTOCOL</h1>
        <p class="subtitle">Access Required</p>
        <form method="post">
            <input type="password" name="password" placeholder="Enter password" autofocus required>
            <button type="submit">Enter Arena</button>
            {% if error %}
            <p class="error">{{ error }}</p>
            {% endif %}
        </form>
    </div>
</body>
</html>
'''


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login page - password gate for the entire site"""
    if request.method == 'POST':
        if request.form.get('password') == SITE_PASSWORD:
            session['authenticated'] = True
            return redirect('/')
        return render_template_string(LOGIN_PAGE, error="Incorrect password. Try again.")
    return render_template_string(LOGIN_PAGE, error=None)


@app.route('/logout')
def logout():
    """Clear session and redirect to login"""
    session.clear()
    return redirect('/login')


@app.route('/robots.txt')
def robots():
    """Tell search engines to stay away"""
    return "User-agent: *\nDisallow: /", 200, {'Content-Type': 'text/plain'}


# Timing configuration
TIMING = {
    'fast': {
        'exchange_delay': 0.3,      # Seconds between exchanges
        'round_break': 2,           # Seconds between rounds
        'post_event_delay': 0.05,   # Small delay after each event
    },
    'normal': {
        'exchange_delay': 1.0,
        'round_break': 5,
        'post_event_delay': 0.1,
    },
    'realtime': {
        'exchange_delay': 12.0,     # ~15 exchanges over 3 minutes
        'round_break': 60,
        'post_event_delay': 0.2,
    }
}


@app.route('/')
@login_required
def index():
    """Main page - NOW PROTECTED"""
    return render_template('index.html')


@app.route('/model-test')
@login_required
def model_test():
    """3D Model Test Page - NOW PROTECTED"""
    return render_template('model_test.html')


@app.route('/api/version')
def get_version():
    """Return current app version - PUBLIC (no auth needed)"""
    return jsonify({'version': APP_VERSION})


@app.route('/debug/env')
def debug_env():
    """Debug route to check environment variables"""
    return jsonify({
        'OPENAI_API_KEY': bool(os.environ.get('OPENAI_API_KEY')),
        'ANTHROPIC_API_KEY': bool(os.environ.get('ANTHROPIC_API_KEY')),
        'SECRET_KEY': bool(os.environ.get('SECRET_KEY')),
        'SITE_PASSWORD': bool(os.environ.get('SITE_PASSWORD')),
        'note': 'All values should be True'
    })


@app.route('/api/fighters')
def get_fighters():
    """Return list of available fighters - PROTECTED"""
    fighters_dir = os.path.join(BASE_DIR, 'data', 'fighters')
    fighters = []
    
    for filename in os.listdir(fighters_dir):
        if filename.endswith('.json'):
            fighter_id = filename[:-5]  # Remove .json
            try:
                fighter = Fighter.from_json(f"data/fighters/{filename}")
                fighters.append({
                    'id': fighter_id,
                    'name': fighter.name
                })
            except Exception as e:
                print(f"Error loading fighter {filename}: {e}")
    
    return jsonify(fighters)


@app.route('/api/simulate/<fighter_a_id>/<fighter_b_id>')
## @login_required
def simulate_fight(fighter_a_id, fighter_b_id):
    """Stream fight simulation using Server-Sent Events - PROTECTED"""
    
    def generate():
        try:
            # Load fighters
            fighter_a = Fighter.from_json(f"data/fighters/{fighter_a_id}.json")
            fighter_b = Fighter.from_json(f"data/fighters/{fighter_b_id}.json")
            
            # Initialize systems
            simulator = MuayThaiSimulatorV2(fighter_a, fighter_b, real_time=False)
            renderer = Renderer2D()
            renderer.init(fighter_a.name, fighter_b.name, config={
                'fighter_a_id': fighter_a_id,
                'fighter_b_id': fighter_b_id
            })
            
            timing = TIMING['fast']
            
            # Try to generate trash talk (may fail if no API key)
            trash_talk = None
            try:
                trash_talk_system = TrashTalkSystem(fighter_a, fighter_b)
                trash_talk = trash_talk_system.generate_weigh_in()
            except Exception as e:
                print(f"Trash talk generation failed: {e}")
            
            # Send initial setup
            yield _sse_message({
                'type': 'setup',
                'fighter_a': {
                    'id': fighter_a_id,
                    'name': fighter_a.name,
                },
                'fighter_b': {
                    'id': fighter_b_id,
                    'name': fighter_b.name,
                },
                'trash_talk': trash_talk,
            })
            
            # Small delay for setup
            time.sleep(0.5)
            
            # If we have trash talk, give time to read it
            if trash_talk:
                time.sleep(3)
            
            # Run simulation
            last_round = 0
            match_gen = simulator.simulate_match_streaming()
            
            try:
                while True:
                    event = next(match_gen)
                    
                    # Pass event to renderer
                    renderer.handle_event(event)
                    
                    # Determine what to send to browser based on event type
                    if event.event_type == EventType.MATCH_START:
                        yield _sse_message({
                            'type': 'match_start',
                            'fighter_a_name': event.fighter_a_name,
                            'fighter_b_name': event.fighter_b_name,
                        })
                        
                    elif event.event_type == EventType.ROUND_START:
                        last_round = event.round_num
                        yield _sse_message({
                            'type': 'round_start',
                            'round': event.round_num,
                        }, event_type='round_start')
                        time.sleep(0.5)
                        
                    elif event.event_type == EventType.STATE_UPDATE:
                        # TBD:  NEW: Send the actual state update event directly
                        yield _sse_message({
                            'type': 'state_update',
                            'round_num': event.round_num,
                            'fighter_a_pos_x': event.fighter_a_pos_x,
                            'fighter_b_pos_x': event.fighter_b_pos_x,
                            'fighter_a_pos_z': event.fighter_a_pos_z,
                            'fighter_b_pos_z': event.fighter_b_pos_z,
                            # ... other fields
                        }, event_type='state_update')
                        time.sleep(0.1)  # Small delay

                        # Render current frame and send
                        frame = renderer.render(timing['exchange_delay'])
                        frame['type'] = 'frame'
                        yield _sse_message(frame)
                        time.sleep(timing['exchange_delay'])
                        
                    elif event.event_type == EventType.STRIKE:
                        # Send strike event for immediate visual feedback
                        yield _sse_message({
                            'type': 'strike',
                            'event': event_to_dict(event),
                        }, event_type='strike')
                        time.sleep(timing['post_event_delay'])
                        
                    elif event.event_type == EventType.CLINCH:
                        yield _sse_message({
                            'type': 'clinch',
                            'event': event_to_dict(event),
                        })
                        time.sleep(timing['post_event_delay'])
                        
                    elif event.event_type == EventType.CLINCH_EXIT:
                        yield _sse_message({
                            'type': 'clinch_exit',
                            'event': event_to_dict(event),
                        })
                        
                    elif event.event_type == EventType.KNOCKDOWN:
                        yield _sse_message({
                            'type': 'knockdown',
                            'event': event_to_dict(event),
                        })
                        time.sleep(1.0)
                        
                    elif event.event_type == EventType.KNOCKDOWN:
                        yield _sse_message({
                            'type': 'fighter_down',
                            'event': event_to_dict(event),
                        })
                        time.sleep(0.5)
                        
                    elif event.event_type == EventType.RECOVERY:
                        yield _sse_message({
                            'type': 'fighter_recovered',
                            'event': event_to_dict(event),
                        })
                        time.sleep(0.5)
                        
                    elif event.event_type == EventType.ROUND_END:
                        yield _sse_message({
                            'type': 'round_end',
                            'round': event.round_num,
                            'fighter_a_score': event.fighter_a_score,
                            'fighter_b_score': event.fighter_b_score,
                        }, event_type='round_end')
                        time.sleep(1.0)
                        
                    elif event.event_type == EventType.BREAK_START:
                        yield _sse_message({
                            'type': 'break',
                            'duration': event.duration_seconds,
                        })
                        # Send keepalives during break
                        for _ in range(timing['round_break']):
                            time.sleep(1)
                            yield _sse_message({'type': 'keepalive'})
                        
                    elif event.event_type == EventType.MATCH_END:
                        yield _sse_message({
                            'type': 'fight_end',
                            'winner': event.winner_name,
                            'method': event.method,
                            'fighter_a_score': event.fighter_a_total_score,
                            'fighter_b_score': event.fighter_b_total_score,
                        }, event_type='fight_end')
                        
            except StopIteration:
                pass
            
            # Final message
            yield _sse_message({'type': 'complete'})
            
        except FileNotFoundError as e:
            yield _sse_message({
                'type': 'error',
                'message': f'Fighter not found: {str(e)}'
            })
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            yield _sse_message({
                'type': 'error',
                'message': f'Simulation error: {str(e)}'
            })
    
    return Response(generate(), mimetype='text/event-stream')


def _sse_message(data: dict, event_type: str = None) -> str:
    """Format data as Server-Sent Event message"""
    if event_type:
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"
    return f"data: {json.dumps(data)}\n\n"


@app.route('/api/fighter/<fighter_id>')
def get_fighter_details(fighter_id):
    """Get detailed info about a specific fighter - PROTECTED"""
    try:
        fighter = Fighter.from_json(f"data/fighters/{fighter_id}.json")
        return jsonify({
            'id': fighter_id,
            'name': fighter.name,
            'stats': {
                'power': fighter.stats.power,
                'speed': fighter.stats.speed,
                'technique': fighter.stats.technique,
                'defense': fighter.stats.defense,
                'cardio': fighter.stats.cardio,
                'clinch': fighter.stats.clinch,
                'chin': fighter.stats.chin,
                'fight_iq': fighter.stats.fight_iq,
            },
            'physical': {
                'height_cm': fighter.physical.height_cm,
                'weight_kg': fighter.physical.weight_kg,
                'age': fighter.physical.age,
            }
        })
    except FileNotFoundError:
        return jsonify({'error': 'Fighter not found'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/models')
def get_models():
    """Return list of available 3D models"""
    models_dir = os.path.join(app.static_folder, 'models')
    models = []
    
    if os.path.exists(models_dir):
        for filename in os.listdir(models_dir):
            if filename.endswith('.glb'):
                models.append({
                    'name': filename.replace('_blender.glb', '').replace('.glb', '').replace('_', ' '),
                    'path': f'/static/models/{filename}'
                })
    
    return jsonify(models)



@app.route('/v2/')
@app.route('/v2/<path:path>')
def serve_react_v2(path=''):
    """
    Serve the React frontend from /v2/
    This allows the React app to run alongside the Flask HTML version
    """
    # If a specific file is requested and exists, serve it
    if path and os.path.exists(os.path.join('static/v2', path)):
        return send_from_directory('static/v2', path)
    
    # Otherwise serve index.html (for client-side routing)
    return send_from_directory('static/v2', 'index.html')


@app.route('/api/generate-fighter', methods=['GET'])
@login_required
def generate_fighter():
    """
    Generate a custom fighter from a text description using Server-Sent Events - PROTECTED
    
    Streams progress updates:
    1. Validation complete
    2. Stats generated
    3. Image being created
    4. Complete
    """
    # Get description from request BEFORE entering generator
    description = request.args.get('description', '').strip()
    
    def generate():
        print(f"🔥 generate_fighter STARTED - description: '{description}'")
        try:
            if not description:
                print("❌ Error: No description provided")
                yield _sse_message({'type': 'error', 'message': 'Description is required'})
                return
            
            if len(description) < 10:
                print(f"❌ Error: Description too short ({len(description)} chars)")
                yield _sse_message({'type': 'error', 'message': 'Description too short (minimum 10 characters)'})
                return
            
            print("📝 Creating FighterGenerator...")
            generator = FighterGenerator()
            print("✓ FighterGenerator created")
            
            # Step 1: Validate
            print("📝 Step 1: Validating description...")
            yield _sse_message({'type': 'progress', 'step': 'validate', 'message': 'Validating fighter description...'})
            
            is_valid = generator._validate_fighter_description(description)
            print(f"✓ Validation result: {is_valid}")
            if not is_valid:
                print("❌ Validation failed")
                yield _sse_message({
                    'type': 'error',
                    'message': 'Please describe a realistic human combat fighter. Descriptions must be plausible martial artists, not animals, fictional creatures, or non-combatants.'
                })
                return
            
            # Step 2: Generate stats
            print("📝 Step 2: Generating fighter attributes...")
            yield _sse_message({'type': 'progress', 'step': 'stats', 'message': 'Generating fighter stats...'})
            
            fighter_data = generator._generate_fighter_attributes(description)
            print(f"✓ Fighter attributes generated: {fighter_data['name']}")
            fighter_id = generator._generate_fighter_id(fighter_data['name'])
            print(f"✓ Fighter ID: {fighter_id}")
            
            # Create Fighter object to get derived stats
            from fighter import Fighter, PhysicalAttributes, TrainingProfile, FightingStyle, Durability, Personality
            
            print("📝 Creating Fighter object...")
            physical = PhysicalAttributes(**fighter_data['physical'])
            training = TrainingProfile(**fighter_data['training'])
            style = FightingStyle(**fighter_data['style'])
            durability = Durability(**fighter_data['durability'])
            personality = Personality(**fighter_data['personality'])
            
            fighter = Fighter(
                fighter_id=fighter_id,
                name=fighter_data['name'],
                discipline=fighter_data['discipline'],
                physical=physical,
                training=training,
                style=style,
                durability=durability,
                personality=personality
            )
            print("✓ Fighter object created")
            
            # Send stats immediately (now with real derived values)
            print("📝 Sending stats to client...")
            yield _sse_message({
                'type': 'stats_ready',
                'fighter_name': fighter.name,
                'fighter_id': fighter.id,
                'stats': {
                    'power': fighter.stats.power,
                    'speed': fighter.stats.speed,
                    'cardio': fighter.stats.cardio,
                },
                'physical': {
                    'height_cm': fighter.physical.height_cm,
                    'weight_kg': fighter.physical.weight_kg,
                    'age': fighter.physical.age,
                }
            })
            print("✓ Stats sent")
            
            # Step 3: Generate image
            print("📝 Step 3: Generating fighter image...")
            yield _sse_message({'type': 'progress', 'step': 'image', 'message': 'Creating fighter image (15-20 seconds)...'})
            
            image_url = generator._generate_fighter_image(fighter_data['image_prompt'])
            print(f"✓ Image generated: {image_url[:50]}...")
            
            # Step 4: Save
            print("📝 Step 4: Saving fighter...")
            yield _sse_message({'type': 'progress', 'step': 'save', 'message': 'Saving fighter...'})
            
            # Save fighter and image
            paths = generator.save_fighter(fighter, image_url, BASE_DIR)
            print(f"✓ Fighter saved: {paths['fighter_path']}")
            print(f"✓ Image saved: {paths['image_path']}")
            
            # Step 5: Complete
            print("📝 Step 5: Sending completion message...")
            yield _sse_message({
                'type': 'complete',
                'fighter_id': fighter.id,
                'fighter_name': fighter.name,
                'image_url': paths['image_url'],
                'stats': {
                    'power': fighter.stats.power,
                    'speed': fighter.stats.speed,
                    'technique': fighter.stats.technique,
                    'defense': fighter.stats.defense,
                    'cardio': fighter.stats.cardio,
                    'clinch': fighter.stats.clinch,
                    'chin': fighter.stats.chin,
                    'fight_iq': fighter.stats.fight_iq,
                },
                'physical': {
                    'height_cm': fighter.physical.height_cm,
                    'weight_kg': fighter.physical.weight_kg,
                    'age': fighter.physical.age,
                }
            })
            print("✅ Fighter generation COMPLETE!")
            
        except ValueError as e:
            print(f"❌ ValueError in fighter generation: {e}")
            import traceback
            traceback.print_exc()
            yield _sse_message({'type': 'error', 'message': str(e)})
        except Exception as e:
            print(f"❌ Exception in fighter generation: {e}")
            import traceback
            traceback.print_exc()
            yield _sse_message({'type': 'error', 'message': f'Generation failed: {str(e)}'})
    
    return Response(generate(), mimetype='text/event-stream')


if __name__ == '__main__':
    # Print version banner
    print_version_banner()
    
    print(f"Working directory: {BASE_DIR}")
    print("Starting server on http://127.0.0.1:5001")
    print("=" * 60)
    
    # Check if credentials are set
    if app.secret_key == 'change-this-in-production-please':
        print("⚠️  WARNING: Using default SECRET_KEY - set SECRET_KEY environment variable!")
    if SITE_PASSWORD == 'fubar':
        print("⚠️  WARNING: Using default password 'fubar' - set SITE_PASSWORD environment variable!")
    
    print("=" * 60)
    
    app.run(debug=False, port=5001, host='127.0.0.1')
