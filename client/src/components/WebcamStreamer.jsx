/**
 * WebcamStreamer Component
 * 
 * Captures webcam video, downscales frames, and sends them to the backend
 * at a controlled frame rate for 3D face reconstruction.
 * 
 * Features:
 * - Live webcam feed display
 * - Frame rate control
 * - Resolution downscaling for performance
 * - Play/pause functionality
 * - Error handling
 */

import React, { useRef, useEffect, useState } from 'react';

const WebcamStreamer = ({ socket, isConnected, onFrame, targetFPS = 10, resolution = 256 }) => {
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const streamRef = useRef(null);
    const animationRef = useRef(null);
    const lastFrameTimeRef = useRef(0);

    const [isStreaming, setIsStreaming] = useState(false);
    const [error, setError] = useState(null);
    const [deviceId, setDeviceId] = useState(null);
    const [devices, setDevices] = useState([]);

    // Initialize webcam
    useEffect(() => {
        initWebcam();

        // Enumerate devices
        navigator.mediaDevices.enumerateDevices()
            .then(devices => {
                const videoDevices = devices.filter(device => device.kind === 'videoinput');
                setDevices(videoDevices);
            });

        return () => {
            stopWebcam();
        };
    }, [deviceId]);

    // Start streaming when connected
    useEffect(() => {
        if (isConnected && isStreaming) {
            startCapture();
        }

        return () => {
            if (animationRef.current) {
                cancelAnimationFrame(animationRef.current);
            }
        };
    }, [isConnected, isStreaming, targetFPS]);

    const initWebcam = async () => {
        try {
            // Request webcam access
            const constraints = {
                video: {
                    deviceId: deviceId ? { exact: deviceId } : undefined,
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: 'user'
                },
                audio: false
            };

            const stream = await navigator.mediaDevices.getUserMedia(constraints);
            streamRef.current = stream;

            if (videoRef.current) {
                videoRef.current.srcObject = stream;
                videoRef.current.play();
                setIsStreaming(true);
                setError(null);
            }
        } catch (err) {
            console.error('Webcam error:', err);
            setError('Failed to access webcam. Please grant camera permissions.');
            setIsStreaming(false);
        }
    };

    const stopWebcam = () => {
        if (streamRef.current) {
            streamRef.current.getTracks().forEach(track => track.stop());
            streamRef.current = null;
        }

        if (animationRef.current) {
            cancelAnimationFrame(animationRef.current);
        }

        setIsStreaming(false);
    };

    const startCapture = () => {
        const canvas = canvasRef.current;
        const video = videoRef.current;

        if (!canvas || !video || !socket || !isConnected) return;

        const ctx = canvas.getContext('2d');
        const frameInterval = 1000 / targetFPS;

        const captureFrame = (timestamp) => {
            // Frame rate throttling
            if (timestamp - lastFrameTimeRef.current < frameInterval) {
                animationRef.current = requestAnimationFrame(captureFrame);
                return;
            }

            lastFrameTimeRef.current = timestamp;

            // Draw video frame to canvas (downscaled)
            ctx.drawImage(video, 0, 0, resolution, resolution);

            // Convert to base64 (JPEG for compression)
            canvas.toBlob((blob) => {
                if (blob && socket) {
                    // Convert blob to base64
                    const reader = new FileReader();
                    reader.onloadend = () => {
                        const base64data = reader.result;

                        // Send to backend
                        socket.emit('frame', { image: base64data });

                        // Notify parent component
                        if (onFrame) {
                            onFrame();
                        }
                    };
                    reader.readAsDataURL(blob);
                }
            }, 'image/jpeg', 0.8);

            // Continue capture loop
            animationRef.current = requestAnimationFrame(captureFrame);
        };

        // Start capture loop
        animationRef.current = requestAnimationFrame(captureFrame);
    };

    const toggleStreaming = () => {
        if (isStreaming) {
            stopWebcam();
        } else {
            initWebcam();
        }
    };

    const changeCamera = (newDeviceId) => {
        setDeviceId(newDeviceId);
        stopWebcam();
    };

    return (
        <div className="webcam-streamer glass-card p-4">
            <div className="flex items-center justify-between mb-3">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Webcam Feed
                </h3>

                <div className="flex items-center gap-2">
                    {/* Camera selector */}
                    {devices.length > 1 && (
                        <select
                            className="px-2 py-1 bg-gray-700 rounded text-sm text-white border border-gray-600"
                            onChange={(e) => changeCamera(e.target.value)}
                            value={deviceId || ''}
                        >
                            {devices.map((device, idx) => (
                                <option key={device.deviceId} value={device.deviceId}>
                                    {device.label || `Camera ${idx + 1}`}
                                </option>
                            ))}
                        </select>
                    )}

                    {/* Start/Stop button */}
                    <button
                        onClick={toggleStreaming}
                        className={`btn ${isStreaming ? 'btn-secondary' : 'btn-primary'}`}
                        disabled={!isConnected}
                    >
                        {isStreaming ? (
                            <>
                                <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                                </svg>
                                Pause
                            </>
                        ) : (
                            <>
                                <svg className="w-4 h-4 inline mr-1" fill="currentColor" viewBox="0 0 20 20">
                                    <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
                                </svg>
                                Start
                            </>
                        )}
                    </button>
                </div>
            </div>

            {error && (
                <div className="mb-3 p-3 bg-red-500/20 border border-red-500/50 rounded text-red-200 text-sm">
                    {error}
                </div>
            )}

            <div className="relative bg-black rounded-lg overflow-hidden aspect-video">
                <video
                    ref={videoRef}
                    className="w-full h-full object-cover"
                    autoPlay
                    playsInline
                    muted
                />

                {!isStreaming && (
                    <div className="absolute inset-0 flex items-center justify-center bg-gray-900/80">
                        <div className="text-center">
                            <svg className="w-16 h-16 mx-auto mb-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                            </svg>
                            <p className="text-gray-400">Camera {isConnected ? 'paused' : 'waiting for connection'}</p>
                        </div>
                    </div>
                )}

                {/* Status indicator */}
                {isStreaming && (
                    <div className="absolute top-3 right-3 flex items-center gap-2 bg-black/50 px-3 py-1 rounded-full">
                        <span className="status-indicator active"></span>
                        <span className="text-xs text-white">LIVE</span>
                    </div>
                )}
            </div>

            {/* Hidden canvas for frame processing */}
            <canvas
                ref={canvasRef}
                width={resolution}
                height={resolution}
                className="hidden"
            />

            {/* Info */}
            <div className="mt-2 text-xs text-gray-400">
                Streaming at {targetFPS} FPS • Resolution: {resolution}×{resolution}
            </div>
        </div>
    );
};

export default WebcamStreamer;
