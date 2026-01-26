# Combat Protocol - System Architecture & Data Flow

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER INTERFACE                           │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  Fighter Creator │              │  Fighter Selector │         │
│  │  (Modal Form)    │              │   (Dropdowns)     │         │
│  └────────┬─────────┘              └─────────┬────────┘         │
│           │                                   │                  │
└───────────┼───────────────────────────────────┼──────────────────┘
            │                                   │
            ▼                                   ▼
┌───────────────────────────────────────────────────────────────────┐
│                      FLASK BACKEND (app.py)                       │
│                                                                   │
│  ┌────────────────────────────┐  ┌────────────────────────────┐ │
│  │ POST /api/generate-fighter │  │ GET /api/fighter/{id}      │ │
│  │  (SSE Stream)              │  │  (Returns fighter JSON)    │ │
│  └──────────┬─────────────────┘  └───────────┬────────────────┘ │
│             │                                 │                  │
└─────────────┼─────────────────────────────────┼──────────────────┘
              │                                 │
              ▼                                 │
┌─────────────────────────────────────┐        │
│  fighter_generator.py               │        │
│  ┌──────────────────────────────┐  │        │
│  │ 1. Validate Description      │  │        │
│  │ 2. Generate Attributes (GPT) │  │        │
│  │ 3. Select 3D Model (GPT)     │◄─┼────────┤
│  │ 4. Generate Image (DALL-E)   │  │        │
│  │ 5. Save Fighter JSON          │  │        │
│  └──────────────────────────────┘  │        │
└──────────────┬──────────────────────┘        │
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATA STORAGE                                  │
│  ┌─────────────────────┐  ┌──────────────────┐  ┌────────────┐ │
│  │ data/fighters/      │  │ static/models/   │  │ static/    │ │
│  │ ├── fighter.json    │  │ ├── library.json │  │ images/    │ │
│  │ │   ├── id          │  │ │                │  │ fighters/  │ │
│  │ │   ├── name        │  │ └── *.glb files  │  │ ├── *.png  │ │
│  │ │   ├── model_3d ───┼──┼────────────────► │  │            │ │
│  │ │   ├── stats       │  │                  │  │            │ │
│  │ │   └── physical    │  │                  │  │            │ │
│  └─────────────────────┘  └──────────────────┘  └────────────┘ │
└───────────────────────────────────────────────────────────────────┘
               │                               │
               │                               │
               ▼                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (index.html)                         │
│                                                                  │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │              THREE.JS 3D VIEWER                            │ │
│  │  ┌──────────────┐              ┌──────────────┐           │ │
│  │  │ Fighter A    │              │ Fighter B    │           │ │
│  │  │ (Red Corner) │              │ (Blue Corner)│           │ │
│  │  │              │              │              │           │ │
│  │  │ Model: ───────────────►  ◄──────── Model: │           │ │
│  │  │ Dynamic GLB  │              │ Dynamic GLB  │           │ │
│  │  └──────────────┘              └──────────────┘           │ │
│  └────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
```

## Detailed Data Flow: Creating Custom Fighter

```
1. USER ACTION
   │
   │ User fills form: "A massive Brazilian heavyweight bruiser"
   │
   ▼
2. FRONTEND (JavaScript)
   │
   │ EventSource: /api/generate-fighter?description=...
   │
   ▼
3. BACKEND (app.py)
   │
   │ Stream SSE events:
   │  - "validate" → Validating...
   │  - "stats" → Generating...
   │  - "image" → Creating image...
   │  - "complete" → Done!
   │
   ▼
4. FIGHTER GENERATOR (fighter_generator.py)
   │
   ├─► GPT-4o-mini: Validate description
   │   Input: "A massive Brazilian heavyweight bruiser"
   │   Output: "YES" (valid description)
   │
   ├─► GPT-4o-mini: Generate attributes
   │   Input: Description
   │   Output: {
   │     name: "Big Dave",
   │     physical: { height: 190, weight: 105, ... },
   │     training: { striking: 800, ... },
   │     style: { ... },
   │     durability: { ... },
   │     personality: { ... }
   │   }
   │
   ├─► GPT-4o-mini: Select 3D model
   │   Input: Description + Physical attrs + Model library
   │   Process:
   │     1. Load model_library.json
   │     2. Format options for GPT:
   │        "Fist Fight B_blender.glb: Stocky brawler, 165-180cm, 75-100kg"
   │        "Punching_blender.glb: Balanced fighter, 170-185cm, 70-90kg"
   │        ...
   │     3. GPT analyzes:
   │        - Height: 190cm → Taller models
   │        - Weight: 105kg → Heavier/stocky models
   │        - "Bruiser" → Brawler style
   │   Output: "Fist Fight B_blender.glb"
   │
   ├─► Extract shorts color
   │   Input: Description
   │   Output: "#FF0000" (if "red" mentioned) or "#000000" (default)
   │
   ├─► DALL-E: Generate image
   │   Input: Enhanced prompt from GPT
   │   Output: Image URL
   │
   └─► Save fighter
       │
       ├─► Create Fighter object with derived stats
       │
       ├─► Save to data/fighters/big_dave.json:
       │   {
       │     "id": "big_dave",
       │     "name": "Big Dave",
       │     "model_3d": "Fist Fight B_blender.glb",  ← AI SELECTED!
       │     "shorts_color": "#FF0000",
       │     "physical": { ... },
       │     "training": { ... },
       │     "derived_stats": { power: 87.5, ... }
       │   }
       │
       └─► Download image to static/images/fighters/big_dave.png
```

## Detailed Data Flow: Selecting Fighter for Preview

```
1. USER ACTION
   │
   │ User selects "Big Dave" from Red Corner dropdown
   │
   ▼
2. FRONTEND EVENT (JavaScript)
   │
   │ fighterASelect.addEventListener('change', async (e) => {
   │   const fighterId = 'big_dave';
   │   await loadFighterModel(fighterId, 'A');
   │ });
   │
   ▼
3. LOAD FIGHTER MODEL (loadFighterModel function)
   │
   ├─► Fetch fighter data
   │   GET /api/fighter/big_dave
   │   Response: {
   │     id: "big_dave",
   │     name: "Big Dave",
   │     model_3d: "Fist Fight B_blender.glb",
   │     shorts_color: "#FF0000",
   │     stats: { ... },
   │     physical: { ... }
   │   }
   │
   ├─► Parse model info
   │   model_filename = "Fist Fight B_blender.glb"
   │   model_path = "/static/models/Fist Fight B_blender.glb"
   │   shorts_color = "#FF0000"
   │
   ├─► Remove old model
   │   if (fighters.A.model exists) {
   │     scene.remove(fighters.A.model)
   │     Clean up mixer and actions
   │   }
   │
   ├─► Load new model
   │   GLTFLoader.load(model_path, (gltf) => {
   │     model = gltf.scene
   │
   │     // Scale to consistent height
   │     bbox = getBoundingBox(model)
   │     scale = 1.8 / bbox.height
   │     model.scale.set(scale, scale, scale)
   │
   │     // Position on correct side
   │     model.position.x = -4  // Red corner (left)
   │     model.position.y = 0   // On ground
   │     model.rotation.y = 0   // Face right
   │
   │     // Apply colors
   │     model.traverse(node => {
   │       if (node.isMesh) {
   │         // Base corner color (orange for red)
   │         node.material.color.set(0xFF6B35)
   │
   │         // Custom shorts color if applicable
   │         if (node.name.includes('short')) {
   │           node.material.color.set(#FF0000)
   │         }
   │       }
   │     })
   │
   │     // Setup animation
   │     if (gltf.animations.length > 0) {
   │       mixer = new AnimationMixer(model)
   │       action = mixer.clipAction(gltf.animations[0])
   │       action.play()
   │     }
   │
   │     scene.add(model)
   │   })
   │
   └─► Store references
       fighters.A = {
         model: model,
         mixer: mixer,
         action: action,
         position: -4,
         rotation: 0,
         color: 0xFF6B35
       }
```

## Model Selection Logic Detail

```
┌─────────────────────────────────────────────────────────────────┐
│                  MODEL SELECTION ALGORITHM                       │
│                   (_select_3d_model method)                      │
└─────────────────────────────────────────────────────────────────┘

INPUT:
  description: "A massive Brazilian heavyweight bruiser"
  physical_attrs: { height: 190, weight: 105 }

PROCESS:
  1. Load model_library.json
     Available models: 7 models with metadata

  2. Format for GPT:
     "Fist Fight B_blender.glb: Stocky brawler, wild style
      Body: stocky, Height: 165-180cm, Weight: 75-100kg"

  3. GPT Analysis:
     Consider:
       ✓ Body type: "bruiser" → stocky
       ✓ Fighting style: "massive" → brawler
       ✓ Height: 190cm → slightly tall (max: 195 in library)
       ✓ Weight: 105kg → heavy (matches Fist Fight B: 75-100kg)

  4. GPT Selection:
     Matches:
       Fist Fight B_blender.glb: ✓✓✓✓ (4/4 criteria)
         - Stocky body type
         - Brawler style
         - Weight range matches
         - "Bruiser" keyword match
       
       Punching_blender.glb: ✓✓ (2/4 criteria)
         - Balanced body type
         - Boxing style
         - Lower weight range

OUTPUT:
  "Fist Fight B_blender.glb"

STORED IN:
  fighter._model_3d = "Fist Fight B_blender.glb"
  
SAVED TO:
  data/fighters/big_dave.json["model_3d"]
```

## File System Structure

```
combat-protocol/
│
├── app.py                          # Flask routes
│   ├── @app.route('/')            # Main page
│   ├── @app.route('/api/fighters') # List all fighters
│   ├── @app.route('/api/fighter/<id>') # Get fighter details
│   └── @app.route('/api/generate-fighter') # Create custom fighter
│
├── fighter_generator.py            # AI-powered generation
│   ├── _validate_fighter_description()
│   ├── _generate_fighter_attributes()  # GPT-4o-mini
│   ├── _select_3d_model()              # GPT-4o-mini ← KEY!
│   ├── _extract_color()
│   ├── _generate_fighter_image()       # DALL-E
│   └── save_fighter()
│
├── fighter.py                      # Fighter class & stats
│   ├── PhysicalAttributes
│   ├── TrainingProfile
│   ├── FightingStyle
│   ├── Durability
│   ├── Personality
│   └── Fighter._derive_stats()    # Calculate combat stats
│
├── static/
│   ├── models/
│   │   ├── model_library.json     # Model metadata ← CRITICAL!
│   │   ├── Boxing_blender.glb
│   │   ├── Punching_blender.glb
│   │   ├── Fist Fight B_blender.glb
│   │   ├── Chapa-Giratoria_blender.glb
│   │   ├── Taunt_blender.glb
│   │   ├── Left Block_blender.glb
│   │   └── Light Hit To Head_blender.glb
│   │
│   └── images/
│       └── fighters/
│           ├── big_dave.png       # AI-generated portraits
│           └── ...
│
├── data/
│   └── fighters/
│       ├── big_dave.json          # Fighter data + model_3d
│       ├── jake_razor.json
│       └── ...
│
└── index.html                      # Frontend with 3D viewer
    ├── Three.js scene setup
    ├── loadFighterModel() function ← NEW!
    ├── Fighter selection dropdowns
    └── 3D preview controls
```

## Key Integration Points

```
┌─────────────────────────────────────────────────────────────────┐
│                    INTEGRATION TOUCHPOINTS                       │
└─────────────────────────────────────────────────────────────────┘

1. BACKEND → MODEL SELECTION
   fighter_generator.py:369
   ────────────────────────────────────
   selected_model = self._select_3d_model(description, fighter_data['physical'])
   fighter_data['model_3d'] = selected_model

2. BACKEND → SAVE TO JSON
   fighter_generator.py:463-464
   ────────────────────────────────────
   if model_3d:
       fighter_json['model_3d'] = model_3d

3. API → SERVE FIGHTER DATA
   app.py:493-513
   ────────────────────────────────────
   fighter = Fighter.from_json(f"data/fighters/{fighter_id}.json")
   return jsonify({ ... })  # Includes model_3d field

4. FRONTEND → FETCH FIGHTER
   index.html (loadFighterModel function)
   ────────────────────────────────────
   const response = await fetch(`/api/fighter/${fighterId}`)
   const fighterData = await response.json()

5. FRONTEND → LOAD MODEL
   index.html (loadFighterModel function)
   ────────────────────────────────────
   const modelFilename = fighterData.model_3d || 'Punching_blender.glb'
   const modelPath = `/static/models/${modelFilename}`
   loader.load(modelPath, ...)

6. 3D RENDERING → DISPLAY
   index.html (Three.js)
   ────────────────────────────────────
   scene.add(model)
   // Model appears in 3D viewer!
```

## Complete Round Trip Example

```
USER: "Create a fast, technical lightweight striker"
  │
  ▼
GPT (Attributes): {
  height: 175cm,
  weight: 68kg,
  muscle_mass: 70%,
  fast_twitch: 85%
}
  │
  ▼
GPT (Model Selection):
  Analyze:
    - Lightweight: 68kg
    - Technical: "precision", "technical"
    - Fast: high fast_twitch
  
  Model Library Check:
    ✓ Light Hit To Head_blender.glb
      Keywords: ["precision", "technical", "striker"]
      Body: lean
      Height: 175-195cm ✓ (175 fits)
      Weight: 65-85kg ✓ (68 fits)
  
  SELECTED: "Light Hit To Head_blender.glb"
  │
  ▼
DALL-E: Generates portrait image
  │
  ▼
SAVE: data/fighters/technical_striker.json
{
  "id": "technical_striker",
  "name": "Lightning Lee",
  "model_3d": "Light Hit To Head_blender.glb",
  "physical": { height: 175, weight: 68, ... },
  "derived_stats": { speed: 92.1, power: 68.0, ... }
}
  │
  ▼
USER: Selects "Lightning Lee" from dropdown
  │
  ▼
FRONTEND: loadFighterModel('technical_striker', 'A')
  │
  ├─► Fetch: GET /api/fighter/technical_striker
  │   Gets: { model_3d: "Light Hit To Head_blender.glb", ... }
  │
  ├─► Load: /static/models/Light Hit To Head_blender.glb
  │   GLTFLoader downloads and parses GLB file
  │
  ├─► Scale: 1.8 units tall (consistent across all fighters)
  │
  ├─► Position: x=-4 (left side, red corner)
  │
  ├─► Color: 0xFF6B35 (orange tint for red corner)
  │
  └─► Display: Lean, technical fighter appears in viewer!
```

This system creates a seamless experience where:
1. AI selects appropriate models automatically
2. Backend stores selections in fighter JSON
3. Frontend dynamically loads whatever the AI chose
4. User sees visually appropriate representation of their fighter!
