# simulator.py (updated version)
import random
import time
from dataclasses import dataclass
from typing import List, Tuple
from fighter import Fighter
from display import TerminalDisplay

@dataclass
class RoundResult:
    """Result of a single round"""
    round_num: int
    fighter_a_score: int
    fighter_b_score: int
    fighter_a_damage_dealt: float
    fighter_b_damage_dealt: float
    fighter_a_stamina_used: float
    fighter_b_stamina_used: float
    exchanges: List[str]
    winner: str  # Name of round winner

@dataclass
class MatchResult:
    """Final result of the match"""
    winner: str
    method: str  # "Decision", "KO", "TKO"
    rounds: List[RoundResult]
    final_scores: Tuple[int, int, int]  # Judge scores for fighter A

class MuayThaiSimulator:
    """Simulates Muay Thai matches using fighter stats"""
    
    def __init__(self, fighter_a: Fighter, fighter_b: Fighter, real_time: bool = False):
        self.fighter_a = fighter_a
        self.fighter_b = fighter_b
        self.real_time = real_time
        
        # Fight state
        self.fighter_a_health = 100.0
        self.fighter_b_health = 100.0
        self.fighter_a_stamina = 100.0
        self.fighter_b_stamina = 100.0
        
        # Damage tracking by type
        self.fighter_a_head_damage = 0.0
        self.fighter_b_head_damage = 0.0
        self.fighter_a_body_damage = 0.0
        self.fighter_b_body_damage = 0.0
        self.fighter_a_leg_damage = 0.0
        self.fighter_b_leg_damage = 0.0
        
        # Display system
        self.display = TerminalDisplay(fighter_a.name, fighter_b.name)
        
    def _get_damage_degradation(self, head_dmg, body_dmg, leg_dmg, durability):
        """Calculate how accumulated damage affects performance"""
        # Head damage affects defense and accuracy
        head_factor = max(0.5, 1.0 - (head_dmg / (100 * durability.head_durability / 100)) * 0.5)
        
        # Body damage affects stamina and power
        body_factor = max(0.6, 1.0 - (body_dmg / (100 * durability.body_durability / 100)) * 0.4)
        
        # Leg damage affects speed and movement
        leg_factor = max(0.7, 1.0 - (leg_dmg / (100 * durability.leg_durability / 100)) * 0.3)
        
        return {
            'defense_mult': head_factor,
            'power_mult': body_factor,
            'stamina_mult': body_factor,
            'speed_mult': leg_factor
        }
    
    def simulate_exchange(self, round_num: int) -> Tuple[str, float, float, float, float]:
        """
        Simulate a single exchange between fighters with damage types.
        Returns: (description, a_damage, b_damage, a_stamina, b_stamina)
        """
        # Get degradation from accumulated damage
        a_degrade = self._get_damage_degradation(
            self.fighter_a_head_damage, 
            self.fighter_a_body_damage,
            self.fighter_a_leg_damage,
            self.fighter_a.durability
        )
        b_degrade = self._get_damage_degradation(
            self.fighter_b_head_damage,
            self.fighter_b_body_damage,
            self.fighter_b_leg_damage,
            self.fighter_b.durability
        )
        
        # Stamina and damage affect performance
        a_effectiveness = (self.fighter_a_stamina / 100.0) * a_degrade['stamina_mult']
        b_effectiveness = (self.fighter_b_stamina / 100.0) * b_degrade['stamina_mult']
        
        # Determine exchange type
        exchange_type = random.choice(['striking', 'clinch', 'defense', 'leg_kick'])
        
        if exchange_type == 'striking':
            # Determine target (head vs body based on fighter preferences)
            a_targets_body = random.random() * 100 < self.fighter_a.style.body_attack_preference
            b_targets_body = random.random() * 100 < self.fighter_b.style.body_attack_preference
            
            # Power punch or regular?
            a_power_punch = random.random() * 100 < self.fighter_a.style.power_punch_frequency
            b_power_punch = random.random() * 100 < self.fighter_b.style.power_punch_frequency
            
            # Calculate attack power (affected by damage)
            a_power_mult = 1.5 if a_power_punch else 1.0
            b_power_mult = 1.5 if b_power_punch else 1.0
            
            a_attack = (self.fighter_a.stats.power * a_degrade['power_mult'] + 
                       self.fighter_a.stats.technique) / 2 * a_effectiveness * a_power_mult
            b_attack = (self.fighter_b.stats.power * b_degrade['power_mult'] + 
                       self.fighter_b.stats.technique) / 2 * b_effectiveness * b_power_mult
            
            # Defense (affected by head damage)
            a_defense = self.fighter_a.stats.defense * a_effectiveness * a_degrade['defense_mult']
            b_defense = self.fighter_b.stats.defense * b_effectiveness * b_degrade['defense_mult']
            
            # Calculate damage
            a_damage_to_b = max(0, (a_attack - b_defense) / 10)
            b_damage_to_a = max(0, (b_attack - a_defense) / 10)
            
            # Apply damage to specific areas
            if a_damage_to_b > 0:
                if a_targets_body:
                    self.fighter_b_body_damage += a_damage_to_b
                else:
                    self.fighter_b_head_damage += a_damage_to_b
                    
            if b_damage_to_a > 0:
                if b_targets_body:
                    self.fighter_a_body_damage += b_damage_to_a
                else:
                    self.fighter_a_head_damage += b_damage_to_a
            
            # Total damage for health bar
            a_damage = a_damage_to_b
            b_damage = b_damage_to_a
            
            # Stamina cost (power punches cost more)
            a_stamina = 3.0 if a_power_punch else 2.0
            b_stamina = 3.0 if b_power_punch else 2.0
            
            # Description
            if a_damage > b_damage * 1.5:
                target = "body shots" if a_targets_body else "head strikes"
                power = "heavy " if a_power_punch else ""
                desc = f"{self.fighter_a.name} lands {power}{target}"
            elif b_damage > a_damage * 1.5:
                target = "body shots" if b_targets_body else "head strikes"
                power = "heavy " if b_power_punch else ""
                desc = f"{self.fighter_b.name} lands {power}{target}"
            else:
                desc = "Even striking exchange"
                
        elif exchange_type == 'leg_kick':
            # Muay Thai leg kicks
            a_kicks = random.random() * 100 < self.fighter_a.style.leg_kick_tendency
            b_kicks = random.random() * 100 < self.fighter_b.style.leg_kick_tendency
            
            if a_kicks and not b_kicks:
                damage = (self.fighter_a.stats.power * a_degrade['power_mult']) / 15
                self.fighter_b_leg_damage += damage
                a_damage = 0
                b_damage = damage
                a_stamina = 2.0
                b_stamina = 1.0
                desc = f"{self.fighter_a.name} lands leg kicks"
            elif b_kicks and not a_kicks:
                damage = (self.fighter_b.stats.power * b_degrade['power_mult']) / 15
                self.fighter_a_leg_damage += damage
                a_damage = damage
                b_damage = 0
                a_stamina = 1.0
                b_stamina = 2.0
                desc = f"{self.fighter_b.name} lands leg kicks"
            else:
                # Both try leg kicks or neither
                a_damage = 1.0
                b_damage = 1.0
                a_stamina = 2.0
                b_stamina = 2.0
                desc = "Trading leg kicks"
                
        elif exchange_type == 'clinch':
            # Clinch skill comparison
            a_clinch = self.fighter_a.stats.clinch * a_effectiveness
            b_clinch = self.fighter_b.stats.clinch * b_effectiveness
            
            # Winner of clinch deals damage (mostly body)
            if a_clinch > b_clinch:
                damage = (a_clinch - b_clinch) / 15
                self.fighter_b_body_damage += damage * 0.7
                self.fighter_b_head_damage += damage * 0.3
                a_damage = 0
                b_damage = damage
                desc = f"{self.fighter_a.name} dominates the clinch"
            else:
                damage = (b_clinch - a_clinch) / 15
                self.fighter_a_body_damage += damage * 0.7
                self.fighter_a_head_damage += damage * 0.3
                a_damage = damage
                b_damage = 0
                desc = f"{self.fighter_b.name} dominates the clinch"
            
            # Clinch is stamina intensive
            a_stamina = 3.0
            b_stamina = 3.0
            
        else:  # defensive exchange
            # Speed + defense (affected by leg damage and head damage)
            a_defense = (self.fighter_a.stats.speed * a_degrade['speed_mult'] + 
                        self.fighter_a.stats.defense * a_degrade['defense_mult']) / 2
            b_defense = (self.fighter_b.stats.speed * b_degrade['speed_mult'] + 
                        self.fighter_b.stats.defense * b_degrade['defense_mult']) / 2
            
            # Minimal damage in defensive round
            a_damage = 0.5
            b_damage = 0.5
            
            # Lower stamina cost
            a_stamina = 1.0
            b_stamina = 1.0
            
            desc = "Cautious exchange, both fighters reset"
        
        return desc, b_damage, a_damage, a_stamina, b_stamina
    
    def format_time(self, seconds: int) -> str:
        """Format seconds as M:SS"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes}:{secs:02d}"
    
    def _get_action_type(self, description: str, fighter_name: str) -> str:
        """Determine action type for visual display based on exchange description"""
        desc_lower = description.lower()
        
        if 'clinch' in desc_lower:
            if fighter_name.lower() in desc_lower and 'dominates' in desc_lower:
                return 'clinch'
            else:
                return 'defend'
        elif 'heavy strikes' in desc_lower:
            if fighter_name.lower() in desc_lower:
                return 'strike'
            else:
                return 'hurt'
        elif 'cautious' in desc_lower or 'reset' in desc_lower:
            return 'defend'
        else:
            return 'idle'
    
    def simulate_round(self, round_num: int, show_realtime: bool = True) -> RoundResult:
        """Simulate one 3-minute round (12-15 exchanges)"""
        exchanges = []
        a_total_damage = 0.0
        b_total_damage = 0.0
        
        num_exchanges = random.randint(12, 15)
        
        # Calculate timing
        if self.real_time:
            round_duration = 180  # 3 minutes in seconds
        else:
            round_duration = 15  # Fast-forward: 15 seconds
        
        time_per_exchange = round_duration / num_exchanges
        
        # Track round score for display
        a_round_score = 10
        b_round_score = 10
        
        for i in range(num_exchanges):
            # Calculate time remaining
            time_remaining = round_duration - (i * time_per_exchange)
            
            desc, a_dmg, b_dmg, a_stam, b_stam = self.simulate_exchange(round_num)
            
            # Apply damage
            self.fighter_a_health -= a_dmg
            self.fighter_b_health -= b_dmg
            
            # Apply stamina drain (affected by cardio)
            cardio_factor_a = self.fighter_a.stats.cardio / 100.0
            cardio_factor_b = self.fighter_b.stats.cardio / 100.0
            
            self.fighter_a_stamina -= a_stam * (1.0 - cardio_factor_a * 0.3)
            self.fighter_b_stamina -= b_stam * (1.0 - cardio_factor_b * 0.3)
            
            # Keep stamina above 0
            self.fighter_a_stamina = max(20, self.fighter_a_stamina)
            self.fighter_b_stamina = max(20, self.fighter_b_stamina)
            
            a_total_damage += a_dmg
            b_total_damage += b_dmg
            exchanges.append(desc)
            
            # Determine fighter actions for visual display
            fighter_a_action = self._get_action_type(desc, self.fighter_a.name)
            fighter_b_action = self._get_action_type(desc, self.fighter_b.name)
            
            # Display exchange in real-time with visual frame
            if show_realtime:
                time_str = self.format_time(int(time_remaining))
                
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
                    'fighter_a_score': a_round_score,
                    'fighter_b_score': b_round_score,
                }
                
                self.display.render_frame(state)
                time.sleep(time_per_exchange)
        
        # Score the round (10-point must system)
        if b_total_damage > a_total_damage * 1.3:
            # Fighter A clearly won
            a_score, b_score = 10, 9
            winner = self.fighter_a.name
        elif a_total_damage > b_total_damage * 1.3:
            # Fighter B clearly won
            a_score, b_score = 9, 10
            winner = self.fighter_b.name
        elif b_total_damage > a_total_damage:
            # Fighter A won close round
            a_score, b_score = 10, 9
            winner = self.fighter_a.name
        elif a_total_damage > b_total_damage:
            # Fighter B won close round
            a_score, b_score = 9, 10
            winner = self.fighter_b.name
        else:
            # Even round
            a_score, b_score = 10, 10
            winner = "Draw"
        
        if show_realtime:
            # Show round end
            self.display.show_round_end({
                'winner': winner,
                'fighter_a_score': a_score,
                'fighter_b_score': b_score
            })
            time.sleep(2)
        
        # Recover some stamina and heal some damage between rounds
        # Recovery rate affects how much
        a_recovery = self.fighter_a.durability.recovery_rate / 100.0
        b_recovery = self.fighter_b.durability.recovery_rate / 100.0
        
        self.fighter_a_stamina = min(100, self.fighter_a_stamina + (15 * a_recovery))
        self.fighter_b_stamina = min(100, self.fighter_b_stamina + (15 * b_recovery))
        
        # Partial recovery of accumulated damage
        self.fighter_a_head_damage = max(0, self.fighter_a_head_damage - (2 * a_recovery))
        self.fighter_b_head_damage = max(0, self.fighter_b_head_damage - (2 * b_recovery))
        self.fighter_a_body_damage = max(0, self.fighter_a_body_damage - (3 * a_recovery))
        self.fighter_b_body_damage = max(0, self.fighter_b_body_damage - (3 * b_recovery))
        self.fighter_a_leg_damage = max(0, self.fighter_a_leg_damage - (2 * a_recovery))
        self.fighter_b_leg_damage = max(0, self.fighter_b_leg_damage - (2 * b_recovery))
        
        return RoundResult(
            round_num=round_num,
            fighter_a_score=a_score,
            fighter_b_score=b_score,
            fighter_a_damage_dealt=b_total_damage,
            fighter_b_damage_dealt=a_total_damage,
            fighter_a_stamina_used=100 - self.fighter_a_stamina,
            fighter_b_stamina_used=100 - self.fighter_b_stamina,
            exchanges=exchanges,
            winner=winner
        )
    
    def simulate_match(self, verbose: bool = True) -> MatchResult:
        """Simulate full 5-round match"""
        rounds = []
        
        if verbose:
            print("\n" + "="*60)
            print(f"MATCH: {self.fighter_a.name} vs {self.fighter_b.name}")
            print("="*60)
            if self.real_time:
                print("Mode: REAL-TIME (3 minutes per round)")
            else:
                print("Mode: FAST-FORWARD (15 seconds per round)")
            print("="*60)
            time.sleep(2)
        
        # Simulate 5 rounds
        for round_num in range(1, 6):
            round_result = self.simulate_round(round_num, show_realtime=verbose)
            rounds.append(round_result)
            
            # Check for KO/TKO
            if self.fighter_a_health < 20:
                if verbose:
                    self.display.show_fight_end({
                        'winner': self.fighter_b.name,
                        'method': f"TKO Round {round_num}"
                    })
                return MatchResult(
                    winner=self.fighter_b.name,
                    method=f"TKO Round {round_num}",
                    rounds=rounds,
                    final_scores=(0, 0, 0)
                )
            elif self.fighter_b_health < 20:
                if verbose:
                    self.display.show_fight_end({
                        'winner': self.fighter_a.name,
                        'method': f"TKO Round {round_num}"
                    })
                return MatchResult(
                    winner=self.fighter_a.name,
                    method=f"TKO Round {round_num}",
                    rounds=rounds,
                    final_scores=(0, 0, 0)
                )
            
            # Break between rounds (except after round 5)
            if round_num < 5 and verbose:
                break_time = 5 if self.real_time else 2
                print(f"\n[{break_time} second break...]")
                time.sleep(break_time)
        
        # Calculate final scores (3 judges)
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
        
        if verbose:
            self.display.show_fight_end({
                'winner': winner,
                'method': method
            })
        
        return MatchResult(
            winner=winner,
            method=method,
            rounds=rounds,
            final_scores=(a_total, a_total, a_total)
        )