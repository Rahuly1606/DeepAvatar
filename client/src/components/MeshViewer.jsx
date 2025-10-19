/**
 * MeshViewer Component
 * 
 * 3D visualization of reconstructed face mesh using Three.js
 * 
 * Features:
 * - Real-time mesh rendering
 * - Orbit controls (rotate, zoom, pan)
 * - Lighting controls
 * - Wireframe toggle
 * - Mesh color customization
 * - Smooth mesh updates
 */

import React, { useRef, useEffect, useState } from 'react';
import * as THREE from 'three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls';

const MeshViewer = ({ meshData, showWireframe, meshColor, lighting }) => {
    const containerRef = useRef(null);
    const sceneRef = useRef(null);
    const cameraRef = useRef(null);
    const rendererRef = useRef(null);
    const controlsRef = useRef(null);
    const meshRef = useRef(null);
    const animationFrameRef = useRef(null);

    const [isInitialized, setIsInitialized] = useState(false);

    // Initialize Three.js scene
    useEffect(() => {
        if (!containerRef.current) return;

        // Scene setup
        const scene = new THREE.Scene();
        scene.background = new THREE.Color(0xffffff);  // Pure white background for academic/research style
        sceneRef.current = scene;

        // Camera setup - slight perspective at eye level for natural portrait view
        const camera = new THREE.PerspectiveCamera(
            45,  // Wider FOV for better visibility
            containerRef.current.clientWidth / containerRef.current.clientHeight,
            0.1,
            2000
        );
        camera.position.set(0, 0, 500);  // Camera at eye level, facing front
        camera.lookAt(0, 0, 0);  // Ensure camera is looking at center
        cameraRef.current = camera;

        // Renderer setup - high quality for research-grade visualization
        const renderer = new THREE.WebGLRenderer({
            antialias: true,
            alpha: false,  // Solid white background
            powerPreference: "high-performance",
            precision: "highp"  // High precision for better quality
        });
        renderer.setSize(containerRef.current.clientWidth, containerRef.current.clientHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        renderer.shadowMap.enabled = false;  // Clean academic look without shadows
        renderer.toneMapping = THREE.ACESFilmicToneMapping;
        renderer.toneMappingExposure = 1.0;
        renderer.outputColorSpace = THREE.SRGBColorSpace;  // Accurate color reproduction
        containerRef.current.appendChild(renderer.domElement);
        rendererRef.current = renderer;

        // Orbit controls - will be enabled/disabled based on mouse position over mesh
        const controls = new OrbitControls(camera, renderer.domElement);
        controls.enableDamping = true;
        controls.dampingFactor = 0.05;
        controls.screenSpacePanning = false;
        controls.minDistance = 100;   // Allow closer zoom
        controls.maxDistance = 1000;  // Allow further zoom
        controls.target.set(0, 0, 0);  // Explicitly set target to origin (center of viewport)
        controls.enabled = false;  // Start disabled, will enable only when over mesh
        controls.update();
        controlsRef.current = controls;

        // Raycaster for detecting mouse over mesh
        const raycaster = new THREE.Raycaster();
        const mouse = new THREE.Vector2();
        let isOverMesh = false;

        // Mouse move handler to detect if cursor is over the mesh
        const onMouseMove = (event) => {
            if (!containerRef.current || !meshRef.current) return;

            const rect = containerRef.current.getBoundingClientRect();
            mouse.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

            raycaster.setFromCamera(mouse, camera);
            const intersects = raycaster.intersectObject(meshRef.current);

            const wasOverMesh = isOverMesh;
            isOverMesh = intersects.length > 0;

            // Enable/disable controls based on whether mouse is over mesh
            if (isOverMesh !== wasOverMesh) {
                controls.enabled = isOverMesh;
                containerRef.current.style.cursor = isOverMesh ? 'grab' : 'default';
            }
        };

        // Mouse down handler to change cursor when dragging
        const onMouseDown = () => {
            if (isOverMesh && containerRef.current) {
                containerRef.current.style.cursor = 'grabbing';
                document.body.style.overflow = 'hidden';  // Prevent page scroll while dragging
            }
        };

        // Mouse up handler to restore cursor
        const onMouseUp = () => {
            if (containerRef.current) {
                containerRef.current.style.cursor = isOverMesh ? 'grab' : 'default';
                document.body.style.overflow = '';  // Restore page scroll
            }
        };

        // Wheel handler - only zoom if over mesh
        const onWheel = (event) => {
            if (!isOverMesh) {
                return;  // Allow normal page scroll
            }
            // If over mesh, prevent page scroll and allow zoom
            event.preventDefault();
            event.stopPropagation();
        };

        // Add event listeners
        renderer.domElement.addEventListener('mousemove', onMouseMove);
        renderer.domElement.addEventListener('mousedown', onMouseDown);
        renderer.domElement.addEventListener('mouseup', onMouseUp);
        renderer.domElement.addEventListener('wheel', onWheel, { passive: false });

        controlsRef.current = controls;

        // Lighting setup
        setupLighting(scene);

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
            controls.update();
            renderer.render(scene, camera);
        };
        animate();

        setIsInitialized(true);

        // Cleanup
        return () => {
            window.removeEventListener('resize', handleResize);

            if (renderer.domElement) {
                renderer.domElement.removeEventListener('mousemove', onMouseMove);
                renderer.domElement.removeEventListener('mousedown', onMouseDown);
                renderer.domElement.removeEventListener('mouseup', onMouseUp);
                renderer.domElement.removeEventListener('wheel', onWheel);
            }

            if (animationFrameRef.current) {
                cancelAnimationFrame(animationFrameRef.current);
            }

            if (containerRef.current && renderer.domElement) {
                containerRef.current.removeChild(renderer.domElement);
            }

            renderer.dispose();
            controls.dispose();
        };
    }, []);

    // Setup lighting
    const setupLighting = (scene) => {
        // Studio lighting setup for research-grade academic visualization
        // Soft, even lighting to reveal subtle surface details without harsh shadows

        // Primary key light - front, slightly elevated (main illumination)
        const keyLight = new THREE.DirectionalLight(0xffffff, 1.0);
        keyLight.position.set(0, 100, 400);
        keyLight.name = 'directional';
        scene.add(keyLight);

        // Secondary fill light - opposite side to soften shadows
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
        fillLight.position.set(-200, 50, 300);
        fillLight.name = 'point';
        scene.add(fillLight);

        // Additional fill from right
        const fillRight = new THREE.DirectionalLight(0xffffff, 0.5);
        fillRight.position.set(200, 50, 300);
        scene.add(fillRight);

        // Soft ambient light for even illumination (research studio quality)
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        ambientLight.name = 'ambient';
        scene.add(ambientLight);

        // Subtle rim light from behind for edge definition
        const rimLight = new THREE.DirectionalLight(0xffffff, 0.2);
        rimLight.position.set(0, 100, -200);
        scene.add(rimLight);
    };

    // Update lighting
    useEffect(() => {
        if (!sceneRef.current || !lighting) return;

        const scene = sceneRef.current;

        const ambientLight = scene.getObjectByName('ambient');
        const directionalLight = scene.getObjectByName('directional');
        const pointLight = scene.getObjectByName('point');

        if (ambientLight) ambientLight.intensity = lighting.ambient;
        if (directionalLight) directionalLight.intensity = lighting.directional;
        if (pointLight) pointLight.intensity = lighting.point;
    }, [lighting]);

    // Update mesh when data changes
    useEffect(() => {
        if (!isInitialized || !meshData || !sceneRef.current) return;

        updateMesh(meshData);
    }, [meshData, isInitialized]);

    // Update wireframe mode
    useEffect(() => {
        if (!meshRef.current) return;

        meshRef.current.material.wireframe = showWireframe;
    }, [showWireframe]);

    // Update mesh color
    useEffect(() => {
        if (!meshRef.current) return;

        meshRef.current.material.color.set(meshColor);
    }, [meshColor]);

    const updateMesh = (data) => {
        if (!data.vertices || !data.faces) return;

        const scene = sceneRef.current;

        // Remove old mesh
        if (meshRef.current) {
            scene.remove(meshRef.current);
            meshRef.current.geometry.dispose();
            meshRef.current.material.dispose();
        }

        // Create geometry from mesh data
        const geometry = new THREE.BufferGeometry();

        // Convert vertices array
        const vertices = new Float32Array(data.vertices.flat());
        geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));

        // Convert faces array
        const indices = new Uint32Array(data.faces.flat());
        geometry.setIndex(new THREE.BufferAttribute(indices, 1));

        // Compute normals for proper lighting
        geometry.computeVertexNormals();

        // Create professional research-grade matte material
        const material = new THREE.MeshStandardMaterial({
            color: meshColor || 0xb0b0b0,  // Light gray for academic/medical visualization
            wireframe: showWireframe,
            flatShading: false,  // Smooth shading for realistic surface
            side: THREE.DoubleSide,
            metalness: 0.0,      // No metallic reflection (pure matte)
            roughness: 0.9,      // Very matte finish for research quality
            emissive: 0x000000,
            emissiveIntensity: 0,
        });

        // Create mesh
        const mesh = new THREE.Mesh(geometry, material);

        // First, center the geometry itself at the origin
        geometry.computeBoundingBox();
        const boundingBox = geometry.boundingBox;
        const center = new THREE.Vector3();
        boundingBox.getCenter(center);

        // Translate geometry vertices to center it at origin
        geometry.translate(-center.x, -center.y, -center.z);

        // Recompute bounding box after translation
        geometry.computeBoundingBox();

        // Calculate the size of the bounding box
        const size = new THREE.Vector3();
        geometry.boundingBox.getSize(size);
        const maxDim = Math.max(size.x, size.y, size.z);

        // Scale mesh to fit in view (target size of ~200 units for better visibility)
        const targetSize = 200;
        const scale = targetSize / maxDim;
        mesh.scale.set(scale, scale, scale);

        // Rotate mesh to be upright and facing forward (3DDFA_V2 coordinate system adjustment)
        mesh.rotation.x = Math.PI;  // Flip vertically (180° around X-axis) to correct upside-down
        mesh.rotation.y = Math.PI;  // Rotate 180° around Y-axis to face camera

        // Position at world origin (0, 0, 0) - center of the viewport
        mesh.position.set(0, 0, 0);

        console.log('[MeshViewer] Mesh created:', {
            vertices: data.vertices.length,
            faces: data.faces.length,
            scale: scale,
            position: mesh.position,
            rotation: { x: mesh.rotation.x, y: mesh.rotation.y, z: mesh.rotation.z },
            boundingBoxSize: size,
            targetSize: targetSize
        });

        meshRef.current = mesh;
        scene.add(mesh);
    };

    const resetView = () => {
        if (!cameraRef.current || !controlsRef.current) return;

        cameraRef.current.position.set(0, 0, 500);  // Match initial camera position
        cameraRef.current.lookAt(0, 0, 0);  // Look at center
        controlsRef.current.target.set(0, 0, 0);
        controlsRef.current.update();
    };

    return (
        <div className="mesh-viewer glass-card p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                    </svg>
                    3D Facial Geometry (Dense Mesh)
                </h3>

                <button
                    onClick={resetView}
                    className="btn btn-outline text-sm tooltip-container"
                    title="Reset camera view"
                >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                    </svg>
                    <span className="tooltip">Reset View</span>
                </button>
            </div>

            <div
                ref={containerRef}
                className="relative bg-white rounded-lg overflow-hidden border border-gray-200"
                style={{
                    height: '500px'
                }}
            >
                {!meshData && (
                    <div className="absolute inset-0 flex items-center justify-center bg-white">
                        <div className="text-center">
                            <div className="pulse mb-4">
                                <svg className="w-16 h-16 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4" />
                                </svg>
                            </div>
                            <p className="text-gray-400">Waiting for face detection...</p>
                        </div>
                    </div>
                )}

                {/* Controls hint */}
                <div className="absolute bottom-3 left-3 bg-gray-800/90 px-3 py-2 rounded text-xs text-white shadow-lg">
                    <div className="font-semibold mb-1">Hover over face to interact:</div>
                    <div>🖱️ Left drag: Rotate</div>
                    <div>🖱️ Right drag: Pan</div>
                    <div>🖱️ Scroll: Zoom</div>
                </div>
            </div>

            <div className="mt-2 flex items-center justify-between text-xs">
                <div className="text-gray-500">
                    Controls active when hovering over mesh
                </div>
                {meshData && (
                    <div className="flex items-center gap-3">
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-green-500"></div>
                            <span className="text-gray-400">
                                {meshData.vertices?.length.toLocaleString() || 0} vertices
                            </span>
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                            <span className="text-gray-400">
                                {meshData.faces?.length.toLocaleString() || 0} faces
                            </span>
                        </div>
                        <div className="px-2 py-0.5 bg-green-500/20 text-green-400 rounded text-xs font-semibold">
                            Dense Mesh
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default MeshViewer;
