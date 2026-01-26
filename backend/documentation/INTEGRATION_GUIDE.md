# Combat Protocol - Dynamic 3D Model Integration

## Overview
This integration connects your AI-generated custom fighters with the 3D visualization system, automatically loading the appropriate 3D model based on fighter attributes.

## What Changed

### 1. Dynamic Model Loading System
Previously, models were hardcoded:
```javascript
const modelPathA = '/static/models/Punching_blender.glb';  // Always this model
const modelPathB = '/static/models/Boxing_with_kick.glb';  // Always this model
```

Now, models are loaded dynamically based on fighter selection:
```javascript
async function loadFighterModel(fighterId, corner) {
    // Fetches fighter JSON
    // Reads model_3d field
    // Loads appropriate model
    // Applies customizations
}
```

### 2. Data Flow

```
User Action: Select Fighter from Dropdown
        ↓
Fetch: /api/fighter/{fighter_id}
        ↓
Response: {
    name: "Big Dave",
    model_3d: "Fist Fight B_blender.glb",
    shorts_color: "#FF0000",
    stats: { ... },
    physical: { ... }
}
        ↓
Load: /static/models/Fist Fight B_blender.glb
        ↓
Apply: Position, rotation, colors
        ↓
Display: Model appears in 3D viewer
```

## Key Functions

### `loadFighterModel(fighterId, corner)`
Main function that handles dynamic model loading.

**Parameters:**
- `fighterId`: The fighter's unique ID (e.g., "big_dave")
- `corner`: Either 'A' (red corner) or 'B' (blue corner)

**What it does:**
1. Fetches fighter data from `/api/fighter/{fighterId}`
2. Extracts `model_3d` field (with fallback to 'Punching_blender.glb')
3. Removes old model from scene if exists
4. Loads new model using GLTFLoader
5. Scales model to consistent height (1.8 units)
6. Positions model on correct side (-4 for red, +4 for blue)
7. Applies corner color (orange for A, teal for B)
8. Optionally applies `shorts_color` if specified
9. Sets up animation if model has animations
10. Adds model to scene

### Model Storage Structure
```javascript
const fighters = {
    A: {
        model: null,        // THREE.Object3D
        mixer: null,        // THREE.AnimationMixer
        action: null,       // THREE.AnimationAction
        position: -4,       // X position (left side)
        rotation: 0,        // Y rotation (facing right)
        color: 0xFF6B35     // Base color (orange)
    },
    B: {
        model: null,
        mixer: null,
        action: null,
        position: 4,        // X position (right side)
        rotation: Math.PI,  // Y rotation (facing left)
        color: 0x10A37F     // Base color (teal)
    }
};
```

## Backend Requirements

### Fighter JSON Structure
Each fighter's JSON file must contain (or will contain after regeneration):

```json
{
  "id": "big_dave",
  "name": "Big Dave",
  "discipline": "Muay Thai",
  "model_3d": "Fist Fight B_blender.glb",
  "shorts_color": "#FF0000",
  "physical": {
    "height_cm": 185,
    "weight_kg": 95,
    ...
  },
  "training": { ... },
  "style": { ... },
  "durability": { ... },
  "personality": { ... },
  "derived_stats": { ... }
}
```

### API Endpoint
The `/api/fighter/{fighter_id}` endpoint must return the fighter JSON with `model_3d` field.

**Your current implementation (app.py lines 488-517)** already does this! It reads from the JSON file, so as long as the JSON contains `model_3d`, it will work.

## Model Library Integration

### model_library.json Structure
Located at `/static/models/model_library.json`:

```json
{
  "Punching_blender.glb": {
    "display_name": "Punching Fighter",
    "keywords": ["puncher", "boxer", "aggressive"],
    "body_type": "balanced",
    "fighting_style": "boxing",
    "stance": "aggressive",
    "height_range_cm": [170, 185],
    "weight_range_kg": [70, 90],
    "description": "Balanced fighter with aggressive punching stance"
  },
  ...
}
```

### AI Selection Process (Already Implemented!)
Your `fighter_generator.py` already has the `_select_3d_model()` method (lines 206-270) that:

1. Takes fighter description and physical attributes
2. Formats available models for GPT
3. Uses GPT-4o-mini to select best matching model
4. Returns model filename
5. Stores in `fighter._model_3d`
6. Saves to JSON via `save_fighter()` method

## Color Customization

### How Shorts Color Works
The system attempts to apply custom colors to model materials:

```javascript
// If shorts color is specified and material name contains "shorts" or "pants"
if (shortsColor && node.name && 
    (node.name.toLowerCase().includes('short') || 
     node.name.toLowerCase().includes('pant'))) {
    node.material.color.set(shortsColor);
}
```

**Note:** This depends on your Blender models having appropriately named materials/meshes. If materials aren't named "shorts" or "pants", the custom color won't apply (but base corner color will still work).

### Fallback Behavior
- **No model_3d field:** Uses 'Punching_blender.glb' as default
- **Invalid model path:** Shows error alert, no model displayed
- **No shorts_color field:** Just uses corner base color (orange/teal)

## Integration Steps

### To Use This New System:

1. **Replace your index.html** with the new version that includes `loadFighterModel()` function

2. **Ensure model_library.json exists** at `/static/models/model_library.json` 
   ✅ You already have this!

3. **Regenerate existing custom fighters** OR manually add `model_3d` field to their JSON files

4. **Test with new custom fighter creation** - the system will automatically select and save the appropriate model

### Backward Compatibility

The system handles missing `model_3d` fields gracefully:
```javascript
const modelFilename = fighterData.model_3d || 'Punching_blender.glb';
```

So old fighters without `model_3d` will just use the default Punching model.

## Testing Checklist

1. ✅ Create a new custom fighter (should auto-select model)
2. ✅ Select fighter from red corner dropdown
3. ✅ Verify correct model loads on left side
4. ✅ Select fighter from blue corner dropdown
5. ✅ Verify correct model loads on right side
6. ✅ Try different fighters with different body types
7. ✅ Verify models change when selection changes
8. ✅ Test animation controls (play/pause)
9. ✅ Test camera reset button

## Debugging

### Console Logs
The system logs extensively:
- Fighter data fetched
- Model path being loaded
- Position calculations
- Animation setup
- Any errors

### Common Issues

**Model not loading:**
- Check browser console for errors
- Verify model file exists at `/static/models/{filename}`
- Check that fighter JSON has `model_3d` field
- Verify API endpoint `/api/fighter/{id}` returns data

**Wrong model appearing:**
- Check fighter JSON `model_3d` field value
- Verify model filename matches file in `/static/models/`
- Check `model_library.json` for typos

**Colors not applying:**
- Base corner colors (orange/teal) always work
- Shorts colors only work if mesh names contain "short" or "pant"
- Check Blender model mesh/material names

**Animations not playing:**
- Verify GLB file contains animations
- Check console for animation mixer setup messages
- Some models may not have animations (they'll just pose)

## Advanced: Mesh Naming for Color Customization

To enable full shorts color customization, your Blender models should follow this naming convention:

```
FighterBody (mesh)
├── Body (mesh) 
├── Head (mesh)
├── Shorts (mesh)  ← Will receive custom color
├── Gloves (mesh)
└── Feet (mesh)
```

Or alternatively:
```
FighterBody (mesh)
├── Body (mesh)
├── Head (mesh) 
├── Pants (mesh)  ← Will receive custom color
├── Gloves (mesh)
└── Feet (mesh)
```

You can update this in Blender by renaming objects/materials accordingly.

## Future Enhancements

Potential improvements:
1. **Material-specific coloring:** Apply different colors to gloves, shorts, skin tone
2. **Model scaling based on height:** Taller fighters = bigger models
3. **Stance variations:** Load different idle poses based on fighting style
4. **Dynamic textures:** Apply AI-generated textures to models
5. **Blend shapes:** Morph body proportions based on physical attributes
6. **Equipment variations:** Add/remove gear (headgear, shin guards, etc.)

## File Structure Summary

```
combat-protocol/
├── app.py                          # Flask backend (already good!)
├── fighter_generator.py            # AI generation with model selection (already good!)
├── static/
│   ├── models/
│   │   ├── model_library.json     # Model metadata (already exists!)
│   │   ├── Punching_blender.glb
│   │   ├── Boxing_blender.glb
│   │   ├── Fist Fight B_blender.glb
│   │   └── ... (other models)
│   └── images/
│       └── fighters/               # AI-generated fighter images
├── data/
│   └── fighters/                   # Fighter JSON files
│       ├── big_dave.json          # Contains model_3d field
│       └── ... (other fighters)
└── index.html                      # Frontend (REPLACE with new version)
```

## Summary

This integration is **fully automated** once in place:

1. User describes fighter → AI selects appropriate 3D model
2. User selects fighter → System automatically loads correct model
3. Model appears in preview → Positioned, colored, and animated
4. Everything works seamlessly together!

The beauty is that you don't need to manually specify models - the AI does it based on fighter attributes, and the frontend just displays whatever the AI chose.
