# trash_talk.py
import json
import requests
from typing import Dict, Any

class TrashTalkSystem:
    """Generate contextual trash talk using Claude API"""
    
    def __init__(self, fighter_a, fighter_b):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        
    def _call_claude_api(self, prompt: str) -> str:
        """Call Claude API to generate trash talk"""
        try:
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "Content-Type": "application/json",
                },
                json={
                    "model": "claude-sonnet-4-20250514",
                    "max_tokens": 150,
                    "messages": [
                        {"role": "user", "content": prompt}
                    ]
                }
            )
            
            data = response.json()
            
            # Extract text from response
            if 'content' in data and len(data['content']) > 0:
                return data['content'][0]['text'].strip()
            else:
                return "[Fighter stares silently]"
                
        except Exception as e:
            print(f"Trash talk generation error: {e}")
            return "[Fighter remains focused]"
    
    def _build_fighter_context(self, fighter) -> str:
        """Build context string about a fighter"""
        return f"""
Fighter: {fighter.name}
Discipline: {fighter.discipline}
Stats: Power {fighter.stats.power}, Speed {fighter.stats.speed}, Cardio {fighter.stats.cardio}
Style: {"Body puncher" if fighter.style.body_attack_preference > 60 else "Headhunter"}
Personality:
  - Confidence: {fighter.personality.confidence}/100 ({"cocky" if fighter.personality.confidence > 70 else "humble" if fighter.personality.confidence < 40 else "balanced"})
  - Aggression: {fighter.personality.aggression}/100 ({"angry" if fighter.personality.aggression > 70 else "calm" if fighter.personality.aggression < 40 else "controlled"})
  - Respect: {fighter.personality.respect}/100 ({"respectful" if fighter.personality.respect > 60 else "disrespectful"})
  - Humor: {fighter.personality.humor}/100 ({"joker" if fighter.personality.humor > 60 else "serious"})
"""
    
    def generate_weigh_in(self) -> Dict[str, str]:
        """Generate pre-fight weigh-in trash talk"""
        
        # Build context for both fighters
        context = f"""You are generating pre-fight weigh-in trash talk for a brutal Muay Thai match on an adult betting platform.

{self._build_fighter_context(self.fighter_a)}

{self._build_fighter_context(self.fighter_b)}

Generate AGGRESSIVE, INTENSE trash talk for the weigh-in face-off. This is R-RATED content for adults.

Guidelines:
- Use profanity naturally (fuck, shit, ass, damn, hell, bastard)
- Be aggressive and confrontational
- Reference violence and domination
- Make it feel like real fighters about to go to war
- Each fighter speaks 1-2 sentences reflecting their personality
- Cocky fighters should be arrogant and disrespectful
- Humble fighters can be confident without being loud
- Aggressive fighters should threaten violence

Format your response as JSON:
{{
  "fighter_a": "quote here",
  "fighter_b": "quote here"
}}

Only return the JSON, nothing else."""

        response = self._call_claude_api(context)
        
        # Parse JSON response
        try:
            trash_talk = json.loads(response)
            return {
                'fighter_a': trash_talk.get('fighter_a', f"{self.fighter_a.name}: I'm going to fucking destroy you."),
                'fighter_b': trash_talk.get('fighter_b', f"{self.fighter_b.name}: Bring it on, you son of a bitch.")
            }
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return {
                'fighter_a': f"{self.fighter_a.name}: I'm ready to break you.",
                'fighter_b': f"{self.fighter_b.name}: Let's see what you got, tough guy."
            }
    
    def generate_between_rounds(self, round_num: int, fight_state: Dict[str, Any]) -> Dict[str, str]:
        """Generate trash talk between rounds"""
        
        context = f"""Generate corner advice for round {round_num + 1} of a Muay Thai fight.

{self._build_fighter_context(self.fighter_a)}
Current state: Health {fight_state['fighter_a_health']:.1f}%, Stamina {fight_state['fighter_a_stamina']:.1f}%

{self._build_fighter_context(self.fighter_b)}
Current state: Health {fight_state['fighter_b_health']:.1f}%, Stamina {fight_state['fighter_b_stamina']:.1f}%

Generate 1 sentence of corner advice for each fighter based on how the fight is going.

Format as JSON:
{{
  "fighter_a_corner": "advice here",
  "fighter_b_corner": "advice here"
}}

Only return the JSON."""

        response = self._call_claude_api(context)
        
        try:
            advice = json.loads(response)
            return {
                'fighter_a': advice.get('fighter_a_corner', "Stay focused!"),
                'fighter_b': advice.get('fighter_b_corner', "Keep pressing!")
            }
        except json.JSONDecodeError:
            return {
                'fighter_a': f"{self.fighter_a.name}'s corner: Keep it up!",
                'fighter_b': f"{self.fighter_b.name}'s corner: Stay strong!"
            }
    
    def generate_post_fight(self, winner_name: str, loser_name: str, method: str) -> Dict[str, str]:
        """Generate post-fight speeches"""
        
        winner = self.fighter_a if self.fighter_a.name == winner_name else self.fighter_b
        loser = self.fighter_b if self.fighter_a.name == winner_name else self.fighter_a
        
        context = f"""Generate post-fight interviews after a Muay Thai match.

Winner: {winner.name}
Victory method: {method}
{self._build_fighter_context(winner)}

Loser: {loser.name}
{self._build_fighter_context(loser)}

Generate 1-2 sentence victory speech and 1-2 sentence gracious defeat response.

Format as JSON:
{{
  "winner": "victory speech here",
  "loser": "defeat response here"
}}

Only return the JSON."""

        response = self._call_claude_api(context)
        
        try:
            speeches = json.loads(response)
            return {
                'winner': speeches.get('winner', f"{winner_name}: Great fight!"),
                'loser': speeches.get('loser', f"{loser_name}: I'll be back stronger.")
            }
        except json.JSONDecodeError:
            return {
                'winner': f"{winner_name}: I trained hard for this victory.",
                'loser': f"{loser_name}: Congratulations to my opponent."
            }
