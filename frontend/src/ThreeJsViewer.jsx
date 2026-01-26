import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import './ThreeJsViewer.css';

// API base URL - matches api.js configuration
// Use localhost for development, production domain otherwise
const isDevelopment = import.meta.env.DEV;
const API_BASE_URL = isDevelopment 
  ? 'http://localhost:5001'  // Local Flask backend
  : window.location.origin;   // Production: https://combatprotocol.com

console.log('ThreeJsViewer API_BASE_URL:', API_BASE_URL, '(isDevelopment:', isDevelopment, ')');

function ThreeJsViewer({ fighterA, fighterB, fightData = null }) {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null); // ADD THIS - store OrbitControls
  const modelARef = useRef(null);
  const modelBRef = useRef(null);
  const mixerARef = useRef(null);
  const mixerBRef = useRef(null);
  const animationFrameRef = useRef(null);
  const clockRef = useRef(new THREE.Clock());
  
  const [isPlaying, setIsPlaying] = useState(false); // Start paused so we can test controls
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    // Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);
    sceneRef.current = scene;

    // Camera setup - CLOSER for better view
    const camera = new THREE.PerspectiveCamera(
      50,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 1.8, 4); // Closer camera (z=4 instead of 8)
    camera.lookAt(0, 1, 0); // Look at center height of fighters
    cameraRef.current = camera;

    // Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // OrbitControls - allows click and drag to rotate camera
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enabled = true; // Explicitly enable
    controls.enableDamping = true; // Smooth movement
    controls.dampingFactor = 0.05;
    controls.enableZoom = true; // Explicitly enable zoom
    controls.enableRotate = true; // Explicitly enable rotation
    controls.enablePan = true; // Explicitly enable panning
    controls.target.set(0, 1, 0); // Look at fighter center
    controls.update();
    controlsRef.current = controls; // STORE IN REF
    
    console.log('🎮 OrbitControls initialized and enabled');

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight1 = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight1.position.set(5, 10, 5);
    directionalLight1.castShadow = true;
    directionalLight1.shadow.camera.near = 0.1;
    directionalLight1.shadow.camera.far = 50;
    directionalLight1.shadow.camera.left = -10;
    directionalLight1.shadow.camera.right = 10;
    directionalLight1.shadow.camera.top = 10;
    directionalLight1.shadow.camera.bottom = -10;
    directionalLight1.shadow.mapSize.width = 2048;
    directionalLight1.shadow.mapSize.height = 2048;
    scene.add(directionalLight1);

    const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.4);
    directionalLight2.position.set(-5, 8, -5);
    scene.add(directionalLight2);

    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(20, 20);
    const groundMaterial = new THREE.MeshStandardMaterial({
      color: 0x1a1a2e,
      roughness: 0.8,
      metalness: 0.2
    });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    ground.receiveShadow = true;
    scene.add(ground);

    // TEST CUBE - Visible reference point
    const testCubeGeometry = new THREE.BoxGeometry(0.5, 0.5, 0.5);
    const testCubeMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xff00ff, // Bright magenta - impossible to miss
      emissive: 0xff00ff,
      emissiveIntensity: 0.5
    });
    const testCube = new THREE.Mesh(testCubeGeometry, testCubeMaterial);
    testCube.position.set(0, 0.25, 0); // Center of scene, on ground
    scene.add(testCube);
    console.log('🟪 TEST CUBE added at center - if you see magenta cube, rendering works!');

    // Ring boundary lines
    const ringGeometry = new THREE.RingGeometry(3.8, 4, 32);
    const ringMaterial = new THREE.MeshBasicMaterial({
      color: 0xff4444,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.3
    });
    const ring = new THREE.Mesh(ringGeometry, ringMaterial);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = 0.01;
    scene.add(ring);

    // Handle window resize
    const handleResize = () => {
      if (!containerRef.current) return;
      
      const width = containerRef.current.clientWidth;
      const height = containerRef.current.clientHeight;
      
      camera.aspect = width / height;
      camera.updateProjectionMatrix();
      renderer.setSize(width, height);
    };
    window.addEventListener('resize', handleResize);

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);
      
      const delta = clockRef.current.getDelta();
      
      // Update OrbitControls
      if (controlsRef.current) {
        controlsRef.current.update();
      }
      
      // Update animation mixers
      if (mixerARef.current && isPlaying) {
        mixerARef.current.update(delta);
      }
      if (mixerBRef.current && isPlaying) {
        mixerBRef.current.update(delta);
      }
      
      // Auto-rotate camera (disabled if user is interacting with controls)
      if (isPlaying && controlsRef.current && !controlsRef.current.enabled) {
        const time = Date.now() * 0.0001;
        camera.position.x = Math.sin(time) * 4; // Match closer camera distance
        camera.position.z = Math.cos(time) * 4;
        camera.position.y = 1.8; // Keep height consistent
        camera.lookAt(0, 1, 0); // Look at fighter center
      }
      
      renderer.render(scene, camera);
    };
    animate();

    // Cleanup
    return () => {
      window.removeEventListener('resize', handleResize);
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (controlsRef.current) {
        controlsRef.current.dispose(); // Cleanup controls
      }
      if (rendererRef.current && containerRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
      renderer.dispose();
    };
  }, []);

  // Load fighter models when fighters change
  useEffect(() => {
    if (!fighterA || !fighterB || !sceneRef.current) return;

    setIsLoading(true);
    setError(null);

    const loader = new GLTFLoader();
    const baseModelPath = `${API_BASE_URL}/static/models/Punching_blender.glb`;

    // Remove old models
    if (modelARef.current) {
      sceneRef.current.remove(modelARef.current);
      modelARef.current = null;
    }
    if (modelBRef.current) {
      sceneRef.current.remove(modelBRef.current);
      modelBRef.current = null;
    }

    let loadedCount = 0;
    const totalToLoad = 2;

    const onLoadComplete = () => {
      loadedCount++;
      if (loadedCount === totalToLoad) {
        setIsLoading(false);
      }
    };

    // Load Fighter A (Red Corner - Left side)
    loader.load(
      baseModelPath,
      (gltf) => {
        console.log('✅ Fighter A model loaded successfully', gltf);
        const model = gltf.scene;
        
        // Calculate bounding box to understand model size
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        console.log('Fighter A model size:', size);
        console.log('Fighter A model center:', center);
        
        // FULL SIZE - much more visible!
        model.scale.set(1, 1, 1);
        model.position.set(-1.5, 0, 0);
        model.rotation.y = Math.PI / 4;
        
        // Make VERY visible for debugging
        model.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
            child.visible = true; // Explicitly set visible
            
            console.log('Fighter A mesh found:', child.name, child.geometry);
            console.log('  - Material:', child.material);
            console.log('  - Visible:', child.visible);
            
            // Ensure material exists and is visible
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(mat => {
                  mat.visible = true;
                  mat.side = THREE.DoubleSide; // Render both sides
                  mat.needsUpdate = true;
                });
              } else {
                child.material.visible = true;
                child.material.side = THREE.DoubleSide;
                child.material.needsUpdate = true;
              }
            }
          }
        });

        sceneRef.current.add(model);
        modelARef.current = model;
        console.log('Fighter A added to scene - should be BRIGHT RED at x=-1.5');
        
        // DEBUG: Log entire scene to see what's actually there
        console.log('📦 SCENE CONTENTS:', sceneRef.current.children.map(child => ({
          name: child.name || child.type,
          type: child.type,
          position: child.position,
          visible: child.visible
        })));

        // Setup animations if available
        if (gltf.animations && gltf.animations.length > 0) {
          console.log('Fighter A has animations:', gltf.animations.length);
          const mixer = new THREE.AnimationMixer(model);
          mixerARef.current = mixer;
          const action = mixer.clipAction(gltf.animations[0]);
          action.play();
        }

        onLoadComplete();
      },
      (progress) => {
        console.log('Loading Fighter A:', (progress.loaded / progress.total * 100).toFixed(0) + '%');
      },
      (error) => {
        console.error('❌ Error loading Fighter A model:', error);
        setError(`Failed to load ${fighterA.name} model`);
        onLoadComplete();
      }
    );

    // Load Fighter B (Blue Corner - Right side)
    loader.load(
      baseModelPath,
      (gltf) => {
        console.log('✅ Fighter B model loaded successfully', gltf);
        const model = gltf.scene;
        
        // Calculate bounding box to understand model size
        const box = new THREE.Box3().setFromObject(model);
        const size = box.getSize(new THREE.Vector3());
        const center = box.getCenter(new THREE.Vector3());
        console.log('Fighter B model size:', size);
        console.log('Fighter B model center:', center);
        
        // FULL SIZE - much more visible!
        model.scale.set(1, 1, 1);
        model.position.set(1.5, 0, 0);
        model.rotation.y = -Math.PI / 4 + Math.PI;
        
        // Make VERY visible for debugging
        model.traverse((child) => {
          if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
            child.visible = true; // Explicitly set visible
            
            console.log('Fighter B mesh found:', child.name, child.geometry);
            console.log('  - Material:', child.material);
            console.log('  - Visible:', child.visible);
            
            // Ensure material exists and is visible
            if (child.material) {
              if (Array.isArray(child.material)) {
                child.material.forEach(mat => {
                  mat.visible = true;
                  mat.side = THREE.DoubleSide; // Render both sides
                  mat.needsUpdate = true;
                });
              } else {
                child.material.visible = true;
                child.material.side = THREE.DoubleSide;
                child.material.needsUpdate = true;
              }
            }
          }
        });

        sceneRef.current.add(model);
        modelBRef.current = model;
        console.log('Fighter B added to scene - should be BRIGHT BLUE at x=1.5');

        // Setup animations if available
        if (gltf.animations && gltf.animations.length > 0) {
          console.log('Fighter B has animations:', gltf.animations.length);
          const mixer = new THREE.AnimationMixer(model);
          mixerBRef.current = mixer;
          const action = mixer.clipAction(gltf.animations[0]);
          action.play();
        }

        onLoadComplete();
      },
      (progress) => {
        console.log('Loading Fighter B:', (progress.loaded / progress.total * 100).toFixed(0) + '%');
      },
      (error) => {
        console.error('❌ Error loading Fighter B model:', error);
        setError(`Failed to load ${fighterB.name} model`);
        onLoadComplete();
      }
    );
  }, [fighterA, fighterB]);

  // Update fighter positions during fight
  useEffect(() => {
    if (!fightData || !modelARef.current || !modelBRef.current) return;

    // Update positions based on fight data
    if (fightData.fighter_a_pos_x !== undefined) {
      // Map simulation position (-5 to 5) to 3D space
      const mappedX = (fightData.fighter_a_pos_x / 5) * 3;
      modelARef.current.position.x = mappedX;
    }

    if (fightData.fighter_b_pos_x !== undefined) {
      const mappedX = (fightData.fighter_b_pos_x / 5) * 3;
      modelBRef.current.position.x = mappedX;
    }
  }, [fightData]);

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handleResetCamera = () => {
    if (cameraRef.current && controlsRef.current) {
      cameraRef.current.position.set(0, 1.8, 4);
      cameraRef.current.lookAt(0, 1, 0);
      controlsRef.current.target.set(0, 1, 0);
      controlsRef.current.update();
    }
  };

  return (
    <div className="threejs-viewer-container">
      <div className="threejs-viewer-header">
        <h2>🥊 3D Fighter Preview</h2>
        {error && <div className="threejs-error">{error}</div>}
      </div>
      
      <div ref={containerRef} className="threejs-canvas-container">
        {isLoading && (
          <div className="threejs-loading">
            <div className="spinner"></div>
            <p>Loading 3D models...</p>
          </div>
        )}
        
        {/* Fighter labels */}
        <div className="threejs-fighter-labels">
          <div className="threejs-fighter-label red">
            {fighterA?.name || 'Select Red Corner'}
          </div>
          <div className="threejs-fighter-label blue">
            {fighterB?.name || 'Select Blue Corner'}
          </div>
        </div>
      </div>

      <div className="threejs-controls">
        <button 
          className="threejs-control-btn" 
          onClick={handlePlayPause}
        >
          {isPlaying ? '⏸️ Pause' : '▶️ Play'}
        </button>
        <button 
          className="threejs-control-btn" 
          onClick={handleResetCamera}
        >
          🔄 Reset Camera
        </button>
      </div>
    </div>
  );
}

export default ThreeJsViewer;
