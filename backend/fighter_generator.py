# fighter_generator.py
"""
AI-powered fighter generation using OpenAI GPT-4o-mini (for stats) and DALL-E (for visuals).
With retry logic for improved reliability.
"""

import os
import json
import openai
from fighter import Fighter, PhysicalAttributes, TrainingProfile, FightingStyle, Durability, Personality
from typing import Dict, Tuple
import base64
import requests
import time
from functools import wraps


def retry_with_backoff(max_retries=3, base_delay=1.0):
    """
    Decorator to retry a function with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay between retries (doubles each time)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            delay = base_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (openai.APIError, requests.RequestException) as e:
                    last_exception = e
                    
                    if attempt < max_retries:
                        print(f"API call failed (attempt {attempt + 1}/{max_retries + 1}): {e}")
                        print(f"Retrying in {delay:.1f} seconds...")
                        time.sleep(delay)
                        delay *= 2  # Exponential backoff
                    else:
                        print(f"API call failed after {max_retries + 1} attempts")
                        raise last_exception
            
            raise last_exception
        return wrapper
    return decorator


class FighterGenerator:
    """Generate custom fighters from text descriptions using AI"""
    
    def __init__(self):
        self.openai_client = openai.OpenAI(
            api_key=os.environ.get("OPENAI_API_KEY")
        )
        
        # Load 3D model library
        model_library_path = os.path.join(
            os.path.dirname(__file__), 
            'static', 
            'models', 
            'model_library.json'
        )
        
        if os.path.exists(model_library_path):
            with open(model_library_path, 'r') as f:
                self.model_library = json.load(f)
        else:
            print(f"Warning: Model library not found at {model_library_path}")
            self.model_library = {}
    
    def generate_fighter(self, description: str, fighter_id: str = None) -> Tuple[Fighter, str]:
        """
        Generate a complete fighter from a text description.
        
        Args:
            description: User's text description of the fighter
            fighter_id: Optional ID, will be auto-generated if not provided
            
        Returns:
            Tuple of (Fighter object, image_url)
        """
        # Step 0: Validate that description is appropriate for a combat fighter
        if not self._validate_fighter_description(description):
            raise ValueError(
                "Please describe a realistic human combat fighter. "
                "Descriptions must be plausible martial artists, not animals, fictional creatures, or non-combatants."
            )
        
        # Step 1: Use GPT-4o-mini to parse description and generate fighter attributes
        fighter_data = self._generate_fighter_attributes(description)
        
        # Step 2: Use DALL-E to generate fighter image
        image_url = self._generate_fighter_image(fighter_data['image_prompt'])
        
        # Step 3: Create Fighter object
        if fighter_id is None:
            fighter_id = self._generate_fighter_id(fighter_data['name'])
        
        physical = PhysicalAttributes(
            height_cm=fighter_data['physical']['height_cm'],
            weight_kg=fighter_data['physical']['weight_kg'],
            age=fighter_data['physical']['age'],
            muscle_mass_percent=fighter_data['physical']['muscle_mass_percent'],
            fast_twitch_ratio=fighter_data['physical']['fast_twitch_ratio']
        )
        
        training = TrainingProfile(
            striking_hours=fighter_data['training']['striking_hours'],
            clinch_hours=fighter_data['training']['clinch_hours'],
            cardio_hours=fighter_data['training']['cardio_hours'],
            sparring_hours=fighter_data['training']['sparring_hours']
        )
        
        style = FightingStyle(
            body_attack_preference=fighter_data['style']['body_attack_preference'],
            leg_kick_tendency=fighter_data['style']['leg_kick_tendency'],
            power_punch_frequency=fighter_data['style']['power_punch_frequency']
        )
        
        durability = Durability(
            head_durability=fighter_data['durability']['head_durability'],
            body_durability=fighter_data['durability']['body_durability'],
            leg_durability=fighter_data['durability']['leg_durability'],
            recovery_rate=fighter_data['durability']['recovery_rate']
        )
        
        personality = Personality(
            trash_talk_frequency=fighter_data['personality']['trash_talk_frequency'],
            confidence=fighter_data['personality']['confidence'],
            aggression=fighter_data['personality']['aggression'],
            respect=fighter_data['personality']['respect'],
            humor=fighter_data['personality']['humor'],
            verbosity=fighter_data['personality']['verbosity']
        )
        
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
        
        # Store model selection for later use
        fighter._model_3d = fighter_data.get('model_3d')
        fighter._shorts_color = fighter_data.get('shorts_color')
        
        return fighter, image_url
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    def _validate_fighter_description(self, description: str) -> bool:
        """
        Validate that the description is appropriate for a realistic combat fighter.
        Returns True if valid, False if inappropriate.
        """
        prompt = f"""Is this description appropriate for a realistic human combat fighter in a martial arts betting platform?

Description: "{description}"

Respond with ONLY "YES" or "NO".

BE PERMISSIVE - Accept vague or simple descriptions as long as they could describe a human fighter.

Valid descriptions include:
- ANY human martial artists of any style, nationality, build, or experience level
- Simple/vague descriptions like "big dude", "tough guy", "fighter", "small fast person"
- Realistic physical descriptions (tall, muscular, lean, aggressive, technical, etc.)
- Creative but plausible fighters (elderly master, street fighter, etc.)

ONLY reject truly invalid descriptions:
- Animals (cats, dogs, bears, etc.)
- Fictional creatures (dragons, aliens, robots, etc.)
- Non-combatants (babies, toddlers, inanimate objects)
- Obvious joke/nonsense descriptions

When in doubt, say YES.

Response (YES or NO):"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a permissive validator for combat fighter descriptions. When in doubt, accept the description. Respond only with YES or NO."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10,
                temperature=0
            )
            
            response_text = response.choices[0].message.content.strip().upper()
            return response_text == "YES"
        except Exception as e:
            print(f"Validation error: {e}")
            # On error, be permissive - don't block valid requests due to API issues
            return True
    
    @retry_with_backoff(max_retries=2, base_delay=1.0)
    def _select_3d_model(self, description: str, physical_attrs: Dict) -> str:
        """
        Use GPT to select the best matching 3D model based on fighter description.
        
        Args:
            description: User's fighter description
            physical_attrs: Dict with height_cm, weight_kg, etc.
            
        Returns:
            Filename of selected model (e.g., "Boxing_blender.glb")
        """
        if not self.model_library:
            # Fallback if no model library
            return "Punching_blender.glb"
        
        # Format model options for GPT
        model_options = "\n".join([
            f"- {filename}: {data['description']}\n  Keywords: {', '.join(data['keywords'])}\n  Body: {data['body_type']}, Height: {data['height_range_cm']}cm, Weight: {data['weight_range_kg']}kg"
            for filename, data in self.model_library.items()
        ])
        
        prompt = f"""Select the MOST appropriate 3D fighter model based on this description and physical attributes.

Fighter Description: {description}
Height: {physical_attrs['height_cm']}cm
Weight: {physical_attrs['weight_kg']}kg

Available 3D Models:
{model_options}

Return ONLY the exact filename (e.g., "Boxing_blender.glb") that best matches this fighter.

Consider:
1. Body type match (muscular/lean/stocky/balanced)
2. Fighting style implied by description (boxer, kicker, brawler, defensive, etc.)
3. Height and weight ranges
4. Keywords matching description

Respond with ONLY the filename, nothing else:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You select 3D models for fighters. Respond ONLY with the exact filename."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=50,
                temperature=0
            )
            
            selected_model = response.choices[0].message.content.strip()
            
            # Validate selection
            if selected_model not in self.model_library:
                print(f"Warning: Invalid model selection '{selected_model}', using default")
                # Use first available model as fallback
                selected_model = list(self.model_library.keys())[0]
            
            return selected_model
        
        except Exception as e:
            print(f"Model selection error: {e}")
            # Fallback to first available model
            return list(self.model_library.keys())[0] if self.model_library else "Punching_blender.glb"
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _generate_fighter_attributes(self, description: str) -> Dict:
        """Use GPT-4o-mini to parse description and generate realistic fighter attributes"""
        
        prompt = f"""Based on this fighter description, generate realistic physical attributes, training profile, and personality:

"{description}"

CRITICAL: You must respond with ONLY valid JSON. No markdown code blocks, no explanations, no preamble, no postamble. Just the raw JSON object.

{{
  "name": "Fighter's name",
  "discipline": "Muay Thai",
  "physical": {{
    "height_cm": 175.0,
    "weight_kg": 70.0,
    "age": 28,
    "muscle_mass_percent": 75.0,
    "fast_twitch_ratio": 60.0
  }},
  "training": {{
    "striking_hours": 800,
    "clinch_hours": 400,
    "cardio_hours": 600,
    "sparring_hours": 500
  }},
  "style": {{
    "body_attack_preference": 40.0,
    "leg_kick_tendency": 50.0,
    "power_punch_frequency": 45.0
  }},
  "durability": {{
    "head_durability": 70.0,
    "body_durability": 70.0,
    "leg_durability": 70.0,
    "recovery_rate": 60.0
  }},
  "personality": {{
    "trash_talk_frequency": 50.0,
    "confidence": 60.0,
    "aggression": 50.0,
    "respect": 60.0,
    "humor": 40.0,
    "verbosity": 50.0
  }},
  "image_prompt": "A detailed DALL-E prompt for generating the fighter's image"
}}

Guidelines:
- If user says "heavyweight", weight should be 90-110kg, height 180-195cm
- If user says "lightweight", weight should be 60-70kg, height 165-178cm  
- If user says "muscular/strong", muscle_mass_percent should be 80-90
- If user says "lean/fast", muscle_mass_percent should be 65-75
- If user says "young", age 21-25; "experienced/veteran", age 32-38
- Training hours should reflect experience level (beginner: 200-400 each, elite: 800-1200 each)
- All percentage values must be 0-100
- image_prompt should describe: build, stance, ethnicity if mentioned, gear (Muay Thai shorts, gloves), pose (fighting stance), style (realistic illustration, action pose, professional quality)

OUTPUT ONLY THE JSON OBJECT. DO NOT include ```json or ``` or any other text."""

        response = self.openai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a martial arts expert who generates detailed fighter profiles in JSON format. Respond ONLY with valid JSON, no markdown formatting."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.7
        )
        
        # Extract JSON from response
        response_text = response.choices[0].message.content.strip()
        
        # More aggressive cleanup of markdown and extra text
        # Remove any markdown code blocks
        if "```" in response_text:
            # Extract content between first { and last }
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}')
            if start_idx != -1 and end_idx != -1:
                response_text = response_text[start_idx:end_idx+1]
        
        # If still has markdown, try splitting
        if response_text.startswith("```"):
            parts = response_text.split("```")
            for part in parts:
                part = part.strip()
                if part.startswith("json"):
                    part = part[4:].strip()
                if part.startswith("{") and part.endswith("}"):
                    response_text = part
                    break
        
        try:
            fighter_data = json.loads(response_text)
            
            # Add 3D model selection
            selected_model = self._select_3d_model(description, fighter_data['physical'])
            fighter_data['model_3d'] = selected_model
            
            # Optional: Add shorts color (simple extraction)
            fighter_data['shorts_color'] = self._extract_color(description)
            
            return fighter_data
        except json.JSONDecodeError as e:
            print(f"JSON Parse Error: {e}")
            print(f"Response text: {response_text[:500]}")  # Print first 500 chars for debugging
            raise ValueError(f"Failed to parse fighter data. Invalid JSON response from AI.")
    
    @retry_with_backoff(max_retries=3, base_delay=2.0)
    def _generate_fighter_image(self, prompt: str) -> str:
        """Use DALL-E to generate fighter image"""
        
        # Enhance prompt with style specifications
        full_prompt = f"{prompt}, Muay Thai fighter, professional illustration style, clean background, action pose, high quality, detailed"
        
        response = self.openai_client.images.generate(
            model="dall-e-3",
            prompt=full_prompt,
            size="1024x1024",
            quality="standard",
            n=1,
        )
        
        image_url = response.data[0].url
        return image_url
    
    def _generate_fighter_id(self, name: str) -> str:
        """Generate a URL-safe fighter ID from name"""
        import re
        # Convert to lowercase, replace spaces with underscores, remove special chars
        fighter_id = name.lower()
        fighter_id = re.sub(r'[^a-z0-9\s-]', '', fighter_id)
        fighter_id = re.sub(r'[\s-]+', '_', fighter_id)
        return fighter_id
    
    def _extract_color(self, description: str) -> str:
        """
        Extract shorts color from description.
        Returns hex color code.
        """
        color_map = {
            'red': '#FF0000',
            'blue': '#0000FF',
            'black': '#000000',
            'white': '#FFFFFF',
            'green': '#00FF00',
            'yellow': '#FFFF00',
            'purple': '#800080',
            'orange': '#FFA500',
            'gold': '#FFD700',
            'silver': '#C0C0C0'
        }
        
        desc_lower = description.lower()
        for color_name, hex_code in color_map.items():
            if color_name in desc_lower:
                return hex_code
        
        # Default to black
        return '#000000'
    
    def save_fighter(self, fighter: Fighter, image_url: str, base_dir: str = ".", model_3d: str = None, shorts_color: str = None) -> Dict:
        """
        Save fighter JSON and download image to local filesystem.
        
        Args:
            fighter: Fighter object to save
            image_url: URL of fighter image
            base_dir: Base directory for saving files
            model_3d: 3D model filename (optional, will be added to JSON)
            shorts_color: Shorts color hex code (optional, will be added to JSON)
        
        Returns:
            Dict with 'fighter_path', 'image_path', and 'image_url'
        """
        # Ensure directories exist
        fighters_dir = os.path.join(base_dir, "data", "fighters")
        images_dir = os.path.join(base_dir, "static", "images", "fighters")
        os.makedirs(fighters_dir, exist_ok=True)
        os.makedirs(images_dir, exist_ok=True)
        
        # Save fighter JSON
        fighter_path = os.path.join(fighters_dir, f"{fighter.id}.json")
        fighter.to_json(fighter_path)
        
        # If model_3d or shorts_color provided, add them to the JSON file
        if model_3d or shorts_color:
            with open(fighter_path, 'r') as f:
                fighter_json = json.load(f)
            
            if model_3d:
                fighter_json['model_3d'] = model_3d
            if shorts_color:
                fighter_json['shorts_color'] = shorts_color
            
            with open(fighter_path, 'w') as f:
                json.dump(fighter_json, f, indent=2)
        
        # Download and save image
        image_filename = f"{fighter.id}.png"
        image_path = os.path.join(images_dir, image_filename)
        
        # Retry image download with backoff
        max_retries = 3
        for attempt in range(max_retries):
            try:
                response = requests.get(image_url, timeout=30)
                if response.status_code == 200:
                    with open(image_path, 'wb') as f:
                        f.write(response.content)
                    break
                else:
                    if attempt < max_retries - 1:
                        print(f"Image download failed (attempt {attempt + 1}/{max_retries}): {response.status_code}")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        raise Exception(f"Failed to download image after {max_retries} attempts: {response.status_code}")
            except requests.RequestException as e:
                if attempt < max_retries - 1:
                    print(f"Image download error (attempt {attempt + 1}/{max_retries}): {e}")
                    time.sleep(2 ** attempt)
                else:
                    raise Exception(f"Failed to download image after {max_retries} attempts: {e}")
        
        return {
            'fighter_path': fighter_path,
            'image_path': image_path,
            'image_url': f"/static/images/fighters/{image_filename}"
        }


# Example usage
if __name__ == "__main__":
    generator = FighterGenerator()
    
    # Test generation
    description = "A massive Thai heavyweight bruiser, very strong and aggressive"
    fighter, image_url = generator.generate_fighter(description)
    
    print("Generated fighter:")
    fighter.display_stats()
    print(f"\nImage URL: {image_url}")
    
    # Save to filesystem
    paths = generator.save_fighter(
        fighter, 
        image_url,
        model_3d=getattr(fighter, '_model_3d', None),
        shorts_color=getattr(fighter, '_shorts_color', None)
    )
    print(f"\nSaved to:")
    print(f"  Fighter: {paths['fighter_path']}")
    print(f"  Image: {paths['image_path']}")
    print(f"  3D Model: {getattr(fighter, '_model_3d', 'Not assigned')}")
    print(f"  Shorts Color: {getattr(fighter, '_shorts_color', 'Not assigned')}")
