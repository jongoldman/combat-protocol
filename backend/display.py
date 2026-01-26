# display.py
"""
Visual display system for Combat Protocol fights.
Works in both terminal (with ANSI colors) and web browser (with HTML/CSS).
"""

class FightDisplay:
    """Base class for fight visualization"""
    
    def __init__(self, fighter_a_name, fighter_b_name):
        self.fighter_a_name = fighter_a_name
        self.fighter_b_name = fighter_b_name
    
    def render_frame(self, state):
        """Render a single frame of the fight. Override in subclasses."""
        raise NotImplementedError


class TerminalDisplay(FightDisplay):
    """ASCII/Unicode display for terminal output"""
    
    # ANSI color codes
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    RESET = '\033[0m'
    
    def __init__(self, fighter_a_name, fighter_b_name, use_color=True):
        super().__init__(fighter_a_name, fighter_b_name)
        self.use_color = use_color
    
    def _color(self, text, color_code):
        """Apply color if enabled"""
        if self.use_color:
            return f"{color_code}{text}{self.RESET}"
        return text
    
    def _make_bar(self, value, max_value=100, width=20, filled_char='█', empty_char='░'):
        """Create a visual bar (health/stamina)"""
        filled_count = int((value / max_value) * width)
        filled = filled_char * filled_count
        empty = empty_char * (width - filled_count)
        
        # Color based on value
        if value > 70:
            color = self.GREEN
        elif value > 40:
            color = self.YELLOW
        else:
            color = self.RED
        
        return self._color(filled, color) + empty
    
    def clear_screen(self):
        """Clear terminal screen"""
        print('\033[2J\033[H', end='')
    
    def render_frame(self, state):
        """
        Render fight state to terminal.
        
        state dict should contain:
        - round_num: int
        - time_remaining: str (e.g., "2:45")
        - fighter_a_health: float
        - fighter_b_health: float
        - fighter_a_stamina: float
        - fighter_b_stamina: float
        - action: str (what's happening)
        - fighter_a_score: int (current round score)
        - fighter_b_score: int (current round score)
        """
        # Clear and move to top
        self.clear_screen()
        
        # Title bar
        title = "═" * 70
        print(self._color(title, self.CYAN))
        print(self._color(f"  COMBAT PROTOCOL - ROUND {state['round_num']} - TIME: {state['time_remaining']}", self.BOLD))
        print(self._color(title, self.CYAN))
        print()
        
        # Fighter stats side-by-side
        name_a = self.fighter_a_name[:20].center(30)
        name_b = self.fighter_b_name[:20].center(30)
        
        print(f"  {self._color(name_a, self.BOLD)}    VS    {self._color(name_b, self.BOLD)}")
        print()
        
        # Health bars
        health_a_bar = self._make_bar(state['fighter_a_health'])
        health_b_bar = self._make_bar(state['fighter_b_health'])
        
        print(f"  HP  {health_a_bar} {state['fighter_a_health']:>5.1f}%       {health_b_bar} {state['fighter_b_health']:>5.1f}%")
        print()
        
        # Stamina bars
        stamina_a_bar = self._make_bar(state['fighter_a_stamina'])
        stamina_b_bar = self._make_bar(state['fighter_b_stamina'])
        
        print(f"  STA {stamina_a_bar} {state['fighter_a_stamina']:>5.1f}%       {stamina_b_bar} {state['fighter_b_stamina']:>5.1f}%")
        print()
        
        # Fighter avatars with simple stance
        avatar_a = self._get_avatar(state.get('fighter_a_action', 'idle'))
        avatar_b = self._get_avatar(state.get('fighter_b_action', 'idle'), flipped=True)
        
        print(f"       {avatar_a}                    {avatar_b}")
        print()
        
        # Action description
        action_box = "─" * 70
        print(f"  {action_box}")
        action_text = state['action'].center(68)
        print(f"  │{self._color(action_text, self.YELLOW)}│")
        print(f"  {action_box}")
        print()
        
        # Round score
        print(f"  Round Score: {self.fighter_a_name[:15]} {state['fighter_a_score']} - {state['fighter_b_score']} {self.fighter_b_name[:15]}")
        print()
    
    def _get_avatar(self, action, flipped=False):
        """Return simple ASCII fighter based on action"""
        avatars = {
            'idle': '🥊' if not flipped else '🥊',
            'strike': '👊' if not flipped else '👊',
            'clinch': '🤼' if not flipped else '🤼',
            'defend': '🛡️' if not flipped else '🛡️',
            'hurt': '😵' if not flipped else '😵',
        }
        return avatars.get(action, '🥊')
    
    def show_round_end(self, state):
        """Display round end summary"""
        print()
        print(self._color("═" * 70, self.CYAN))
        print(self._color("  ROUND OVER!", self.BOLD))
        print(self._color(f"  {state['winner']} wins the round", self.GREEN))
        print(self._color(f"  Score: {state['fighter_a_score']}-{state['fighter_b_score']}", self.YELLOW))
        print(self._color("═" * 70, self.CYAN))
        print()
    
    def show_fight_end(self, result):
        """Display final result"""
        print()
        print(self._color("█" * 70, self.CYAN))
        print(self._color("█" * 70, self.CYAN))
        print()
        winner_text = f"WINNER: {result['winner']}".center(70)
        print(self._color(winner_text, self.BOLD + self.GREEN))
        method_text = f"by {result['method']}".center(70)
        print(self._color(method_text, self.YELLOW))
        print()
        print(self._color("█" * 70, self.CYAN))
        print(self._color("█" * 70, self.CYAN))
        print()


class WebDisplay(FightDisplay):
    """HTML display for web browser"""
    
    def __init__(self, fighter_a_name, fighter_b_name):
        super().__init__(fighter_a_name, fighter_b_name)
    
    def _make_bar(self, value, max_value=100):
        """Create HTML progress bar"""
        percentage = (value / max_value) * 100
        
        # Color based on value
        if value > 70:
            color = '#4ade80'  # green
        elif value > 40:
            color = '#fbbf24'  # yellow
        else:
            color = '#ef4444'  # red
        
        return {
            'percentage': percentage,
            'color': color,
            'value': value
        }
    
    def render_frame_html(self, state):
        """
        Render fight state as HTML.
        Returns HTML string ready to be inserted into page.
        """
        health_a = self._make_bar(state['fighter_a_health'])
        health_b = self._make_bar(state['fighter_b_health'])
        stamina_a = self._make_bar(state['fighter_a_stamina'])
        stamina_b = self._make_bar(state['fighter_b_stamina'])
        
        avatar_a = self._get_avatar_html(state.get('fighter_a_action', 'idle'))
        avatar_b = self._get_avatar_html(state.get('fighter_b_action', 'idle'))
        
        html = f'''
        <div class="fight-frame">
            <div class="header">
                <div class="round-info">ROUND {state['round_num']}</div>
                <div class="time-info">{state['time_remaining']}</div>
            </div>
            
            <div class="fighters-container">
                <div class="fighter fighter-a">
                    <div class="fighter-name">{self.fighter_a_name}</div>
                    <div class="stat-bar">
                        <span class="stat-label">HP</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: {health_a['percentage']}%; background: {health_a['color']}"></div>
                        </div>
                        <span class="stat-value">{health_a['value']:.1f}%</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">STA</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: {stamina_a['percentage']}%; background: {stamina_a['color']}"></div>
                        </div>
                        <span class="stat-value">{stamina_a['value']:.1f}%</span>
                    </div>
                    <div class="avatar">{avatar_a}</div>
                </div>
                
                <div class="vs-divider">VS</div>
                
                <div class="fighter fighter-b">
                    <div class="fighter-name">{self.fighter_b_name}</div>
                    <div class="stat-bar">
                        <span class="stat-label">HP</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: {health_b['percentage']}%; background: {health_b['color']}"></div>
                        </div>
                        <span class="stat-value">{health_b['value']:.1f}%</span>
                    </div>
                    <div class="stat-bar">
                        <span class="stat-label">STA</span>
                        <div class="bar-container">
                            <div class="bar-fill" style="width: {stamina_b['percentage']}%; background: {stamina_b['color']}"></div>
                        </div>
                        <span class="stat-value">{stamina_b['value']:.1f}%</span>
                    </div>
                    <div class="avatar">{avatar_b}</div>
                </div>
            </div>
            
            <div class="action-box">
                <div class="action-text">{state['action']}</div>
            </div>
            
            <div class="score-box">
                Round Score: {state['fighter_a_score']} - {state['fighter_b_score']}
            </div>
        </div>
        '''
        
        return html
    
    def _get_avatar_html(self, action):
        """Return emoji/unicode fighter based on action"""
        avatars = {
            'idle': '🥊',
            'strike': '👊',
            'clinch': '🤼',
            'defend': '🛡️',
            'hurt': '😵',
        }
        return avatars.get(action, '🥊')
    
    def get_css(self):
        """Return CSS styles for the fight display"""
        return '''
        .fight-frame {
            background: #ffffff;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 20px;
            margin: 0;
            font-family: 'Courier New', monospace;
            transition: all 0.3s ease;
            color: #1a1a1a;
        }
        
        body.terminal-theme .fight-frame {
            background: #0a0a0a;
            border: 2px solid #00ff00;
            color: #00ff00;
        }
        
        .header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #e5e7eb;
        }
        
        body.terminal-theme .header {
            border-bottom: 2px solid #00ffff;
        }
        
        .round-info, .time-info {
            font-size: 1.5rem;
            font-weight: bold;
            color: #1a1a1a;
        }
        
        body.terminal-theme .round-info,
        body.terminal-theme .time-info {
            color: #00ffff;
        }
        
        .fighters-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin: 30px 0;
        }
        
        .fighter {
            flex: 1;
            text-align: center;
        }
        
        .fighter-name {
            font-size: 1.3rem;
            font-weight: bold;
            margin-bottom: 15px;
            color: #1a1a1a;
        }
        
        body.terminal-theme .fighter-name {
            color: #00ff00;
        }
        
        .vs-divider {
            font-size: 2rem;
            font-weight: bold;
            color: #ff6b6b;
            padding: 0 30px;
        }
        
        body.terminal-theme .vs-divider {
            color: #ffff00;
        }
        
        .stat-bar {
            display: flex;
            align-items: center;
            margin: 10px 0;
            gap: 10px;
        }
        
        .stat-label {
            width: 40px;
            font-weight: bold;
            color: #4b5563;
        }
        
        body.terminal-theme .stat-label {
            color: #00ff00;
        }
        
        .stat-label {
            width: 40px;
            font-weight: bold;
            color: #aaa;
        }
        
        .bar-container {
            flex: 1;
            height: 20px;
            background: #e5e7eb;
            border-radius: 10px;
            overflow: hidden;
        }
        
        body.terminal-theme .bar-container {
            background: rgba(255, 255, 255, 0.1);
        }
        
        .bar-fill {
            height: 100%;
            transition: width 0.3s ease, background 0.3s ease;
            border-radius: 10px;
        }
        
        .stat-value {
            width: 60px;
            text-align: right;
            color: #1a1a1a;
        }
        
        body.terminal-theme .stat-value {
            color: #fff;
        }
        
        .avatar {
            font-size: 4rem;
            margin: 20px 0;
            animation: pulse 0.5s ease-in-out;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.1); }
        }
        
        .action-box {
            background: #f3f4f6;
            border: 2px solid #d1d5db;
            border-radius: 8px;
            padding: 15px;
            margin: 20px 0;
            text-align: left;
        }
        
        body.terminal-theme .action-box {
            background: rgba(255, 255, 0, 0.1);
            border: 1px solid #ffff00;
            text-align: left;
        }
        
        .action-text {
            font-size: 1.2rem;
            color: #1a1a1a;
            font-weight: bold;
        }
        
        body.terminal-theme .action-text {
            color: #ffff00;
        }
        
        .score-box {
            text-align: left;
            font-size: 1.1rem;
            color: #1a1a1a;
            margin-top: 15px;
        }
        
        body.terminal-theme .score-box {
            color: #00ff00;
        }
        '''
