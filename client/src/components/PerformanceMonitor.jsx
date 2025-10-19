/**
 * PerformanceMonitor Component
 * 
 * Displays real-time performance metrics:
 * - FPS (frames per second)
 * - Latency (processing time)
 * - CPU usage
 * - Memory usage
 * - Dropped frames
 */

import React from 'react';

const PerformanceMonitor = ({ metrics, faceDetected }) => {
    const {
        fps = 0,
        avg_latency = 0,
        min_latency = 0,
        max_latency = 0,
        cpu_percent = 0,
        memory_percent = 0,
        dropped_frames = 0
    } = metrics || {};

    // Determine FPS status color
    const getFPSColor = (fps) => {
        if (fps >= 10) return 'text-green-400';
        if (fps >= 5) return 'text-yellow-400';
        return 'text-red-400';
    };

    // Determine latency status color
    const getLatencyColor = (latency) => {
        if (latency < 100) return 'text-green-400';
        if (latency < 200) return 'text-yellow-400';
        return 'text-red-400';
    };

    const MetricCard = ({ icon, label, value, unit, color, tooltip }) => (
        <div className="bg-white/5 rounded-lg p-3 border border-white/10 tooltip-container">
            <div className="flex items-center gap-2 mb-1">
                <span className="text-gray-400">{icon}</span>
                <span className="text-xs text-gray-400">{label}</span>
            </div>
            <div className={`text-2xl font-bold ${color}`}>
                {value}
                <span className="text-sm ml-1">{unit}</span>
            </div>
            {tooltip && <span className="tooltip">{tooltip}</span>}
        </div>
    );

    return (
        <div className="performance-monitor glass-card p-4">
            <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                    </svg>
                    Performance
                </h3>

                {/* Face detection status */}
                <div className="flex items-center gap-2 px-3 py-1 rounded-full bg-white/5">
                    <span className={`status-indicator ${faceDetected ? 'active' : 'inactive'}`}></span>
                    <span className="text-sm text-gray-300">
                        {faceDetected ? 'Face Detected' : 'No Face'}
                    </span>
                </div>
            </div>

            {/* Metrics Grid */}
            <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 mb-4">
                <MetricCard
                    icon="⚡"
                    label="FPS"
                    value={fps.toFixed(1)}
                    unit="fps"
                    color={getFPSColor(fps)}
                    tooltip="Frames processed per second"
                />

                <MetricCard
                    icon="⏱️"
                    label="Latency"
                    value={avg_latency.toFixed(0)}
                    unit="ms"
                    color={getLatencyColor(avg_latency)}
                    tooltip="Average processing time per frame"
                />

                <MetricCard
                    icon="🖥️"
                    label="CPU"
                    value={cpu_percent.toFixed(1)}
                    unit="%"
                    color="text-blue-400"
                    tooltip="Server CPU usage"
                />

                <MetricCard
                    icon="💾"
                    label="Memory"
                    value={memory_percent.toFixed(1)}
                    unit="%"
                    color="text-purple-400"
                    tooltip="Server memory usage"
                />
            </div>

            {/* Detailed Stats */}
            <div className="bg-white/5 rounded-lg p-3 space-y-2">
                <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Latency Range</span>
                    <span className="text-white font-mono">
                        {min_latency.toFixed(0)}ms - {max_latency.toFixed(0)}ms
                    </span>
                </div>

                <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Dropped Frames</span>
                    <span className={`font-mono ${dropped_frames > 10 ? 'text-red-400' : 'text-green-400'}`}>
                        {dropped_frames}
                    </span>
                </div>

                <div className="flex justify-between items-center text-sm">
                    <span className="text-gray-400">Processing Mode</span>
                    <span className="text-white font-semibold">
                        🔵 CPU Only
                    </span>
                </div>
            </div>

            {/* Performance Tips */}
            {(fps < 5 || avg_latency > 200) && (
                <div className="mt-3 p-3 bg-yellow-500/10 border border-yellow-500/30 rounded text-sm text-yellow-200">
                    <div className="flex items-start gap-2">
                        <svg className="w-5 h-5 flex-shrink-0 mt-0.5" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                        </svg>
                        <div>
                            <div className="font-semibold mb-1">Low Performance Detected</div>
                            <ul className="list-disc list-inside text-xs space-y-1">
                                <li>Ensure no heavy background tasks are running</li>
                                <li>Frame skipping is active to maintain smoothness</li>
                                <li>Consider upgrading to GPU mode for better performance</li>
                            </ul>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default PerformanceMonitor;
