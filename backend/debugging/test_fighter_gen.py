import os
print("Testing fighter generation with full logging...")

# Check environment
print(f"\nOPENAI_API_KEY present: {bool(os.environ.get('OPENAI_API_KEY'))}")
print(f"ANTHROPIC_API_KEY present: {bool(os.environ.get('ANTHROPIC_API_KEY'))}")

from fighter_generator import FighterGenerator

try:
    print("\n1. Creating FighterGenerator...")
    gen = FighterGenerator()
    print("   ✓ Success")
    
    print("\n2. Validating description...")
    result = gen._validate_fighter_description("a big strong fighter")
    print(f"   ✓ Validation: {result}")
    
    print("\n3. Generating fighter attributes...")
    fighter_data = gen._generate_fighter_attributes("a big strong fighter")
    print(f"   ✓ Fighter name: {fighter_data['name']}")
    
    print("\n4. Generating image...")
    image_url = gen._generate_fighter_image(fighter_data['image_prompt'])
    print(f"   ✓ Image URL: {image_url[:50]}...")
    
    print("\n✅ ALL STEPS SUCCESSFUL!")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
