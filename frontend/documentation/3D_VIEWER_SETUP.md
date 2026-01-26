# Adding 3D Viewer to Combat Protocol React App

## Step 1: Install Three.js

In your frontend directory, install Three.js:

```bash
cd ~/Downloads/personal/src/combat-protocol-frontend
npm install three
```

## Step 2: Copy the Component Files

Copy these two files into your `src/` directory:
- ThreeJsViewer.jsx
- ThreeJsViewer.css

## Step 3: Update App.jsx

Add the ThreeJsViewer to your App.jsx. Here's where to import it and where to add it:

```jsx
// At the top with other imports
import ThreeJsViewer from './ThreeJsViewer'

// In the JSX, add it between fighter selection and fighter cards:
<>
  {/* Fighter Selection Dropdowns */}
  <div className="fighter-selection">
    {/* ... existing dropdown code ... */}
  </div>

  {/* ADD THE 3D VIEWER HERE */}
  <ThreeJsViewer 
    fighterA={selectedFighters.red} 
    fighterB={selectedFighters.blue}
  />

  {/* Fighter Cards Display */}
  <div className="arena">
    {/* ... existing fighter cards ... */}
  </div>
</>
```

## Step 4: Make Sure Your Model is Accessible

The 3D viewer expects the model at this path:
`/static/models/Punching_blender.glb`

In development, you might need to:
1. Copy your model to `public/static/models/Punching_blender.glb`
2. Or update the path in ThreeJsViewer.jsx line 144 to match where your model is

## Step 5: Run It!

```bash
npm run dev
```

Navigate to http://localhost:5173 and select two fighters. You should see them appear in 3D!

## Features

The 3D viewer includes:
- ✅ Two fighters side-by-side in 3D space
- ✅ Red tint for Fighter A, Blue tint for Fighter B
- ✅ Rotating camera animation (can be paused)
- ✅ Reset camera button
- ✅ Fighter name labels
- ✅ Loading indicator while models load
- ✅ Ground plane and ring boundary
- ✅ Professional lighting setup
- ✅ Shadow casting

## During Fights

When you start a fight and are in the FightSimulator, you can optionally:
1. Pass fight data to ThreeJsViewer to update fighter positions in real-time
2. This requires passing `fightData` prop with `fighter_a_pos_x` and `fighter_b_pos_x`

## Troubleshooting

**Model not loading?**
- Check browser console for errors
- Verify model path matches where file is located
- Make sure model is in `.glb` format

**Black screen?**
- Check that fighters are selected
- Open browser console to see any errors
- Verify Three.js installed correctly: `npm list three`
