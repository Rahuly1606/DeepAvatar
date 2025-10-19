/**
 * Main App Component
 * 
 * Orchestrates the 3D face reconstruction application:
 * - Socket.IO connection management
 * - Component coordination
 * - State management
 * - Real-time data flow
 */

import React, { useState, useEffect, useRef } from 'react';
import { io } from 'socket.io-client';
import WebcamStreamer from './components/WebcamStreamer';
import MeshViewer from './components/MeshViewer';
import PerformanceMonitor from './components/PerformanceMonitor';
import ControlPanel from './components/ControlPanel';

const SOCKET_SERVER = 'http://localhost:5000';

function App() {
    // Socket connection
    const [socket, setSocket] = useState(null);
    const [isConnected, setIsConnected] = useState(false);
    const [connectionError, setConnectionError] = useState(null);

    // 3D mesh data
    const [meshData, setMeshData] = useState(null);

    // Performance metrics
    const [metrics, setMetrics] = useState(null);
    const [faceDetected, setFaceDetected] = useState(false);

    // UI controls
    const [showWireframe, setShowWireframe] = useState(false);
    const [meshColor, setMeshColor] = useState('#b0b0b0');  // Light gray matte for academic/medical visualization
    const [lighting, setLighting] = useState({
        ambient: 0.7,      // Higher ambient for softer, more even lighting
        directional: 1.0,  // Strong key light for clear detail
        point: 0.5         // Moderate fill light
    });

    // Statistics
    const [framesSent, setFramesSent] = useState(0);
    const lastUpdateRef = useRef(Date.now());

    // Initialize Socket.IO connection
    useEffect(() => {
        console.log('Connecting to server...');

        const socketInstance = io(SOCKET_SERVER, {
            transports: ['websocket', 'polling'],
            reconnection: true,
            reconnectionDelay: 1000,
            reconnectionAttempts: 5
        });

        // Connection event handlers
        socketInstance.on('connect', () => {
            console.log('Connected to server');
            setIsConnected(true);
            setConnectionError(null);
        });

        socketInstance.on('disconnect', () => {
            console.log('Disconnected from server');
            setIsConnected(false);
        });

        socketInstance.on('connect_error', (error) => {
            console.error('Connection error:', error);
            setConnectionError('Failed to connect to backend. Make sure the server is running.');
            setIsConnected(false);
        });

        socketInstance.on('connected', (data) => {
            console.log('Server response:', data);
        });

        // Mesh update from server
        socketInstance.on('mesh_update', (data) => {
            setMeshData(data);
            setFaceDetected(data.face_detected || true);

            if (data.metrics) {
                setMetrics(data.metrics);
            }

            lastUpdateRef.current = Date.now();
        });

        // No face detected
        socketInstance.on('no_face', () => {
            setFaceDetected(false);
        });

        // Error from server
        socketInstance.on('error', (data) => {
            console.error('Server error:', data.message);
        });

        // Recalibration confirmation
        socketInstance.on('recalibrated', (data) => {
            console.log('Face tracking reset');
        });

        setSocket(socketInstance);

        // Cleanup on unmount
        return () => {
            socketInstance.disconnect();
        };
    }, []);

    // Handle frame sent callback
    const handleFrameSent = () => {
        setFramesSent(prev => prev + 1);
    };

    // Handle wireframe toggle
    const handleWireframeToggle = () => {
        setShowWireframe(prev => !prev);
    };

    // Handle recalibration
    const handleRecalibrate = () => {
        setMeshData(null);
        setFaceDetected(false);
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 p-4">
            {/* Header */}
            <header className="mb-6">
                <div className="glass-card p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <h1 className="text-3xl font-bold text-white flex items-center gap-3">
                                <svg className="w-8 h-8 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                        d="M14.828 14.828a4 4 0 01-5.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                3D Face Reconstruction
                            </h1>
                            <p className="text-gray-400 mt-1">Real-time facial geometry powered by 3DDFA_V2</p>
                        </div>

                        <div className="text-right">
                            <div className="flex items-center gap-2 mb-1">
                                <span className={`status-indicator ${isConnected ? 'active' : 'error'}`}></span>
                                <span className="text-sm text-gray-300">
                                    {isConnected ? 'Connected' : 'Disconnected'}
                                </span>
                            </div>
                            <div className="text-xs text-gray-500">
                                Frames sent: {framesSent}
                            </div>
                        </div>
                    </div>

                    {connectionError && (
                        <div className="mt-3 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
                            <div className="flex items-center gap-2">
                                <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
                                </svg>
                                {connectionError}
                            </div>
                        </div>
                    )}
                </div>
            </header>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                {/* Left Column - Webcam */}
                <div className="lg:col-span-1">
                    <WebcamStreamer
                        socket={socket}
                        isConnected={isConnected}
                        onFrame={handleFrameSent}
                        targetFPS={10}
                        resolution={256}
                    />
                </div>

                {/* Right Column - 3D Viewer */}
                <div className="lg:col-span-2">
                    <MeshViewer
                        meshData={meshData}
                        showWireframe={showWireframe}
                        meshColor={meshColor}
                        lighting={lighting}
                    />
                </div>
            </div>

            {/* Bottom Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Performance Monitor */}
                <PerformanceMonitor
                    metrics={metrics}
                    faceDetected={faceDetected}
                />

                {/* Control Panel */}
                <ControlPanel
                    onLightingChange={setLighting}
                    onColorChange={setMeshColor}
                    onWireframeToggle={handleWireframeToggle}
                    onRecalibrate={handleRecalibrate}
                    wireframeEnabled={showWireframe}
                    socket={socket}
                />
            </div>

            {/* Footer / About */}
            <footer className="mt-6">
                <div className="glass-card p-4">
                    <div className="flex items-start gap-3">
                        <svg className="w-5 h-5 text-primary-500 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zm-7-4a1 1 0 11-2 0 1 1 0 012 0zM9 9a1 1 0 000 2v3a1 1 0 001 1h1a1 1 0 100-2v-3a1 1 0 00-1-1H9z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <h3 className="text-sm font-semibold text-white mb-1">About This Application</h3>
                            <p className="text-xs text-gray-400 mb-2">
                                This is a real-time 3D face reconstruction system powered by <strong>3DDFA_V2</strong> deep learning model,
                                running completely offline on your local machine. No external APIs or cloud services are used.
                            </p>
                            <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-xs text-gray-500">
                                <div>
                                    <strong className="text-gray-400">Backend:</strong> Flask + PyTorch
                                </div>
                                <div>
                                    <strong className="text-gray-400">Frontend:</strong> React + Three.js
                                </div>
                                <div>
                                    <strong className="text-gray-400">Mode:</strong> CPU-Optimized (ONNX Runtime)
                                </div>
                            </div>
                            <div className="mt-2 text-xs text-gray-500">
                                💡 <strong>Performance Tip:</strong> For better FPS (15-30), enable GPU mode by switching to CUDA device in config.yaml
                            </div>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
}

export default App;
