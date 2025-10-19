/**
 * ControlPanel Component
 * 
 * Interactive UI controls for the 3D face reconstruction app:
 * - Lighting adjustments
 * - Mesh color picker
 * - Wireframe toggle
 * - Recalibrate face detection
 * - Stream pause/resume
 */

import React, { useState } from 'react';

const ControlPanel = ({
    onLightingChange,
    onColorChange,
    onWireframeToggle,
    onRecalibrate,
    wireframeEnabled,
    socket
}) => {
    const [lighting, setLighting] = useState({
        ambient: 0.5,
        directional: 0.8,
        point: 0.5
    });

    const [meshColor, setMeshColor] = useState('#00aaff');
    const [isExpanded, setIsExpanded] = useState(false);

    const handleLightingChange = (type, value) => {
        const newLighting = { ...lighting, [type]: parseFloat(value) };
        setLighting(newLighting);
        if (onLightingChange) onLightingChange(newLighting);
    };

    const handleColorChange = (color) => {
        setMeshColor(color);
        if (onColorChange) onColorChange(color);
    };

    const handleRecalibrate = () => {
        if (socket) {
            socket.emit('recalibrate');
        }
        if (onRecalibrate) onRecalibrate();
    };

    const SliderControl = ({ label, value, onChange, min = 0, max = 1, step = 0.1, tooltip }) => (
        <div className="space-y-1 tooltip-container">
            <div className="flex justify-between items-center">
                <label className="text-sm text-gray-300">{label}</label>
                <span className="text-xs text-gray-400 font-mono">{value.toFixed(1)}</span>
            </div>
            <input
                type="range"
                min={min}
                max={max}
                step={step}
                value={value}
                onChange={(e) => onChange(parseFloat(e.target.value))}
                className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer slider"
            />
            {tooltip && <span className="tooltip">{tooltip}</span>}
        </div>
    );

    return (
        <div className="control-panel glass-card p-4">
            <div
                className="flex items-center justify-between cursor-pointer"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                <h3 className="text-lg font-semibold text-white flex items-center gap-2">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                            d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
                    </svg>
                    Controls
                </h3>

                <svg
                    className={`w-5 h-5 text-gray-400 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
            </div>

            {isExpanded && (
                <div className="mt-4 space-y-6">
                    {/* Lighting Controls */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-white border-b border-white/10 pb-2">
                            💡 Lighting
                        </h4>

                        <SliderControl
                            label="Ambient"
                            value={lighting.ambient}
                            onChange={(value) => handleLightingChange('ambient', value)}
                            tooltip="Soft overall illumination"
                        />

                        <SliderControl
                            label="Directional"
                            value={lighting.directional}
                            onChange={(value) => handleLightingChange('directional', value)}
                            tooltip="Main light source intensity"
                        />

                        <SliderControl
                            label="Point Light"
                            value={lighting.point}
                            onChange={(value) => handleLightingChange('point', value)}
                            tooltip="Fill light intensity"
                        />
                    </div>

                    {/* Mesh Appearance */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-white border-b border-white/10 pb-2">
                            🎨 Appearance
                        </h4>

                        <div className="flex items-center justify-between">
                            <label className="text-sm text-gray-300">Mesh Color</label>
                            <input
                                type="color"
                                value={meshColor}
                                onChange={(e) => handleColorChange(e.target.value)}
                                className="w-12 h-8 rounded cursor-pointer border border-white/20"
                            />
                        </div>

                        <div className="flex items-center justify-between">
                            <label className="text-sm text-gray-300">Wireframe Mode</label>
                            <button
                                onClick={onWireframeToggle}
                                className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${wireframeEnabled ? 'bg-primary-600' : 'bg-gray-700'
                                    }`}
                            >
                                <span
                                    className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${wireframeEnabled ? 'translate-x-6' : 'translate-x-1'
                                        }`}
                                />
                            </button>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-white border-b border-white/10 pb-2">
                            ⚙️ Actions
                        </h4>

                        <button
                            onClick={handleRecalibrate}
                            className="w-full btn btn-outline tooltip-container"
                        >
                            <svg className="w-4 h-4 inline mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                                    d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                            </svg>
                            Recalibrate Face
                            <span className="tooltip">Reset face detection and tracking</span>
                        </button>
                    </div>

                    {/* Presets */}
                    <div className="space-y-3">
                        <h4 className="text-sm font-semibold text-white border-b border-white/10 pb-2">
                            🎭 Lighting Presets
                        </h4>

                        <div className="grid grid-cols-2 gap-2">
                            <button
                                onClick={() => {
                                    const preset = { ambient: 0.8, directional: 0.5, point: 0.3 };
                                    setLighting(preset);
                                    onLightingChange(preset);
                                }}
                                className="btn btn-secondary text-xs"
                            >
                                Soft
                            </button>

                            <button
                                onClick={() => {
                                    const preset = { ambient: 0.3, directional: 1.0, point: 0.5 };
                                    setLighting(preset);
                                    onLightingChange(preset);
                                }}
                                className="btn btn-secondary text-xs"
                            >
                                Dramatic
                            </button>

                            <button
                                onClick={() => {
                                    const preset = { ambient: 0.6, directional: 0.7, point: 0.6 };
                                    setLighting(preset);
                                    onLightingChange(preset);
                                }}
                                className="btn btn-secondary text-xs"
                            >
                                Balanced
                            </button>

                            <button
                                onClick={() => {
                                    const preset = { ambient: 0.5, directional: 0.8, point: 0.5 };
                                    setLighting(preset);
                                    onLightingChange(preset);
                                }}
                                className="btn btn-secondary text-xs"
                            >
                                Default
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default ControlPanel;
