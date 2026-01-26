import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';
import './ThreeJsViewer.css'; // Reuse the same CSS

function ThreeJsTest() {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const controlsRef = useRef(null);
  const cubeRef = useRef(null);
  const animationFrameRef = useRef(null);
  
  const [message, setMessage] = useState('Initializing...');

  // Initialize Three.js scene
  useEffect(() => {
    if (!containerRef.current) return;

    console.log('🎬 Initializing simple Three.js test...');

    // Scene
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0a0a0f);
    sceneRef.current = scene;

    // Camera
    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.set(0, 2, 5);
    camera.lookAt(0, 0, 0);
    cameraRef.current = camera;

    // Renderer
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    containerRef.current.appendChild(renderer.domElement);
    rendererRef.current = renderer;

    // OrbitControls
    const controls = new OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.enabled = true;
    controlsRef.current = controls;
    console.log('✅ OrbitControls enabled');

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(5, 10, 5);
    scene.add(directionalLight);

    // Ground plane
    const groundGeometry = new THREE.PlaneGeometry(10, 10);
    const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x1a1a2e });
    const ground = new THREE.Mesh(groundGeometry, groundMaterial);
    ground.rotation.x = -Math.PI / 2;
    scene.add(ground);

    // TEST CUBE 1 - Red spinning cube at center
    const cubeGeometry = new THREE.BoxGeometry(1, 1, 1);
    const cubeMaterial = new THREE.MeshStandardMaterial({ 
      color: 0xff0000,
      metalness: 0.3,
      roughness: 0.4
    });
    const cube = new THREE.Mesh(cubeGeometry, cubeMaterial);
    cube.position.set(0, 0.5, 0);
    scene.add(cube);
    cubeRef.current = cube;
    console.log('✅ Red cube added at (0, 0.5, 0)');

    // TEST CUBE 2 - Blue cube on the side
    const cube2Material = new THREE.MeshStandardMaterial({ color: 0x0000ff });
    const cube2 = new THREE.Mesh(cubeGeometry, cube2Material);
    cube2.position.set(2, 0.5, 0);
    scene.add(cube2);
    console.log('✅ Blue cube added at (2, 0.5, 0)');

    // TEST CUBE 3 - Green cube on other side
    const cube3Material = new THREE.MeshStandardMaterial({ color: 0x00ff00 });
    const cube3 = new THREE.Mesh(cubeGeometry, cube3Material);
    cube3.position.set(-2, 0.5, 0);
    scene.add(cube3);
    console.log('✅ Green cube added at (-2, 0.5, 0)');

    setMessage('Three cubes loaded! Try dragging to rotate view, scroll to zoom.');

    // Handle resize
    const handleResize = () => {
      if (!containerRef.current) return;
      camera.aspect = containerRef.current.clientWidth / containerRef.current.clientHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
    };
    window.addEventListener('resize', handleResize);

    // Animation loop
    const animate = () => {
      animationFrameRef.current = requestAnimationFrame(animate);
      
      // Rotate the red cube
      if (cubeRef.current) {
        cubeRef.current.rotation.x += 0.01;
        cubeRef.current.rotation.y += 0.01;
      }
      
      // Update controls
      if (controlsRef.current) {
        controlsRef.current.update();
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
        controlsRef.current.dispose();
      }
      if (rendererRef.current && containerRef.current) {
        containerRef.current.removeChild(rendererRef.current.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div className="threejs-viewer-container">
      <div className="threejs-viewer-header">
        <h2>🧪 Three.js Test - Simple Cubes</h2>
      </div>
      
      <div ref={containerRef} className="threejs-canvas-container">
        <div style={{
          position: 'absolute',
          top: '50%',
          left: '50%',
          transform: 'translate(-50%, -50%)',
          color: 'white',
          textAlign: 'center',
          pointerEvents: 'none',
          padding: '20px',
          background: 'rgba(0,0,0,0.7)',
          borderRadius: '8px'
        }}>
          <p>{message}</p>
          <p style={{ fontSize: '0.9rem', marginTop: '10px' }}>
            🖱️ Click and drag to rotate<br/>
            🔍 Scroll to zoom<br/>
            ✋ Right-click and drag to pan
          </p>
        </div>
      </div>

      <div className="threejs-controls">
        <button 
          className="threejs-control-btn"
          onClick={() => {
            if (cameraRef.current) {
              cameraRef.current.position.set(0, 2, 5);
              cameraRef.current.lookAt(0, 0, 0);
              if (controlsRef.current) {
                controlsRef.current.target.set(0, 0, 0);
                controlsRef.current.update();
              }
            }
          }}
        >
          🔄 Reset Camera
        </button>
      </div>
    </div>
  );
}

export default ThreeJsTest;
