# Code Snippets for Integration into Existing index.html

If you prefer to merge the dynamic model loading into your existing index.html rather than replacing it entirely, here are the key code sections to add/modify.

## 1. Add Fighter Model Storage Structure
Add this near the top of your JavaScript (around line 910, where you currently define `modelA` and `modelB`):

```javascript
// REPLACE the existing model variables with this structure:
const fighters = {
    A: {
        model: null,
        mixer: null,
        action: null,
        position: -4,  // Left side
        rotation: 0,
        color: 0xFF6B35  // Anthropic orange / Red corner
    },
    B: {
        model: null,
        mixer: null,
        action: null,
        position: 4,  // Right side
        rotation: Math.PI,  // Face left
        color: 0x10A37F  // OpenAI teal / Blue corner
    }
};

const loader = new GLTFLoader();
const loadingIndicator = document.getElementById('loading-indicator');
```

## 2. Add loadFighterModel Function
Add this complete function (replaces your current model loading code):

```javascript
/**
 * Load a 3D model for a specific fighter corner
 * @param {string} fighterId - The fighter's ID
 * @param {string} corner - Either 'A' (red) or 'B' (blue)
 */
async function loadFighterModel(fighterId, corner) {
    if (!fighterId) {
        console.log(`No fighter selected for corner ${corner}`);
        return;
    }

    try {
        // Show loading indicator
        loadingIndicator.classList.add('active');
        console.log(`Loading fighter ${fighterId} for corner ${corner}...`);

        // Fetch fighter data
        const response = await fetch(`/api/fighter/${fighterId}`);
        if (!response.ok) {
            throw new Error(`Failed to fetch fighter: ${response.statusText}`);
        }
        
        const fighterData = await response.json();
        console.log(`Fighter data:`, fighterData);

        // Get model filename (with fallback to default)
        const modelFilename = fighterData.model_3d || 'Punching_blender.glb';
        const modelPath = `/static/models/${modelFilename}`;
        console.log(`Loading model: ${modelPath}`);

        // Get shorts color (with fallback)
        const shortsColor = fighterData.shorts_color || null;

        // Remove old model if exists
        if (fighters[corner].model) {
            console.log(`Removing old model for corner ${corner}`);
            scene.remove(fighters[corner].model);
            fighters[corner].model = null;
            fighters[corner].mixer = null;
            fighters[corner].action = null;
        }

        // Load new model
        loader.load(
            modelPath,
            (gltf) => {
                console.log(`Model loaded successfully for corner ${corner}`);
                
                const model = gltf.scene;
                fighters[corner].model = model;

                // Scale model to consistent height (1.8 units)
                const box = new THREE.Box3().setFromObject(model);
                const size = box.getSize(new THREE.Vector3());
                const scaleFactor = 1.8 / size.y;
                model.scale.set(scaleFactor, scaleFactor, scaleFactor);

                // Recalculate bounding box after scaling
                box.setFromObject(model);
                const center = box.getCenter(new THREE.Vector3());

                // Position model
                model.position.x = -center.x + fighters[corner].position;
                model.position.y = -box.min.y;  // Place on ground
                model.position.z = -center.z;

                // Rotate model
                model.rotation.y = fighters[corner].rotation;

                console.log(`Model positioned at: ${model.position.x}, ${model.position.y}, ${model.position.z}`);

                // Apply colors to model
                model.traverse((node) => {
                    if (node.isMesh) {
                        node.castShadow = true;
                        node.receiveShadow = true;

                        // Clone material to avoid affecting other instances
                        node.material = node.material.clone();

                        // Apply corner color (base tint)
                        node.material.color.set(fighters[corner].color);

                        // If shorts color is specified and material name contains "shorts" or "pants"
                        if (shortsColor && node.name && 
                            (node.name.toLowerCase().includes('short') || 
                             node.name.toLowerCase().includes('pant'))) {
                            node.material.color.set(shortsColor);
                            console.log(`Applied shorts color ${shortsColor} to ${node.name}`);
                        }
                    }
                });

                // Add model to scene
                scene.add(model);

                // Setup animation if available
                if (gltf.animations && gltf.animations.length > 0) {
                    fighters[corner].mixer = new THREE.AnimationMixer(model);
                    fighters[corner].action = fighters[corner].mixer.clipAction(gltf.animations[0]);
                    fighters[corner].action.setLoop(THREE.LoopRepeat);
                    fighters[corner].action.play();
                    console.log(`Animation started for corner ${corner}`);
                }

                // Hide loading indicator
                loadingIndicator.classList.remove('active');
                console.log(`✅ Fighter ${fighterId} loaded successfully for corner ${corner}`);
            },
            (progress) => {
                // Optional: show loading progress
                console.log(`Loading progress: ${(progress.loaded / progress.total * 100).toFixed(0)}%`);
            },
            (error) => {
                console.error(`Error loading model for corner ${corner}:`, error);
                loadingIndicator.classList.remove('active');
                alert(`Failed to load 3D model: ${modelFilename}\n\nError: ${error.message}`);
            }
        );

    } catch (error) {
        console.error(`Error in loadFighterModel for corner ${corner}:`, error);
        loadingIndicator.classList.remove('active');
        alert(`Failed to load fighter: ${error.message}`);
    }
}
```

## 3. Update Animation Loop
REPLACE your current animation loop mixer updates (around lines 1003-1004):

```javascript
// OLD CODE:
// if (mixerA) mixerA.update(delta);
// if (mixerB) mixerB.update(delta);

// NEW CODE:
if (fighters.A.mixer) fighters.A.mixer.update(delta);
if (fighters.B.mixer) fighters.B.mixer.update(delta);
```

## 4. Update Fighter Selection Event Listeners
REPLACE your current change event listeners (around lines 1052-1060):

```javascript
// OLD CODE:
fighterASelect.addEventListener('change', (e) => {
    const label = document.getElementById('label-fighter-a');
    label.textContent = e.target.options[e.target.selectedIndex].text || 'Select Red Corner';
});

// NEW CODE:
fighterASelect.addEventListener('change', async (e) => {
    const fighterId = e.target.value;
    const label = document.getElementById('label-fighter-a');
    label.textContent = e.target.options[e.target.selectedIndex].text || 'Select Red Corner';
    
    // Load 3D model for Fighter A
    if (fighterId) {
        await loadFighterModel(fighterId, 'A');
    }
    
    checkFightReady();
});

fighterBSelect.addEventListener('change', async (e) => {
    const fighterId = e.target.value;
    const label = document.getElementById('label-fighter-b');
    label.textContent = e.target.options[e.target.selectedIndex].text || 'Select Blue Corner';
    
    // Load 3D model for Fighter B
    if (fighterId) {
        await loadFighterModel(fighterId, 'B');
    }
    
    checkFightReady();
});
```

## 5. Update Preview Control Buttons
REPLACE your preview control event listeners (around lines 1012-1020):

```javascript
// OLD CODE:
document.getElementById('preview-play').addEventListener('click', () => {
    if (actionA) actionA.paused = false;
    if (actionB) actionB.paused = false;
});

document.getElementById('preview-pause').addEventListener('click', () => {
    if (actionA) actionA.paused = true;
    if (actionB) actionB.paused = true;
});

// NEW CODE:
document.getElementById('preview-play').addEventListener('click', () => {
    if (fighters.A.action) fighters.A.action.paused = false;
    if (fighters.B.action) fighters.B.action.paused = false;
});

document.getElementById('preview-pause').addEventListener('click', () => {
    if (fighters.A.action) fighters.A.action.paused = true;
    if (fighters.B.action) fighters.B.action.paused = true;
});
```

## 6. Add Loading Indicator HTML
Add this inside your `#canvas-container` div (around line 678):

```html
<div id="canvas-container">
    <!-- ADD THIS LINE: -->
    <div class="loading-indicator" id="loading-indicator">Loading Model...</div>
    
    <!-- Existing content: -->
    <div class="fighter-3d-labels">
        <div class="fighter-3d-label red" id="label-fighter-a">Select Red Corner</div>
        <div class="fighter-3d-label blue" id="label-fighter-b">Select Blue Corner</div>
    </div>
</div>
```

## 7. Add Loading Indicator CSS
Add this to your stylesheet:

```css
.loading-indicator {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    background: rgba(0, 0, 0, 0.8);
    color: #00ff88;
    padding: 20px 40px;
    border-radius: 8px;
    font-weight: bold;
    z-index: 100;
    display: none;
}

.loading-indicator.active {
    display: block;
}
```

## 8. Remove Old Model Loading Code
DELETE these sections from your existing code:

```javascript
// DELETE THESE LINES (around 915-994):
const modelPathA = '/static/models/Punching_blender.glb';
const modelPathB = '/static/models/Boxing_with_kick.glb';

loader.load(modelPathA, (gltf) => {
    // ... entire Fighter A loading block
});

loader.load(modelPathB, (gltf) => {
    // ... entire Fighter B loading block
});
```

These will be replaced by the dynamic `loadFighterModel()` function that gets called when users select fighters.

## Summary of Changes

**What's being replaced:**
1. Hardcoded model paths → Dynamic loading based on fighter JSON
2. Static model variables → Organized fighter storage structure
3. Load-on-page-load → Load-on-selection

**What stays the same:**
- Scene setup (camera, lights, ground, grid)
- Animation loop structure
- UI controls and layout
- Fight simulation code
- Everything else!

**What's added:**
- `loadFighterModel()` function
- Loading indicator
- Model removal/replacement logic
- Color customization support

The integration is designed to be minimally invasive - you're just swapping out the model loading section while keeping everything else intact.
