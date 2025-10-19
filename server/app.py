"""
Flask + Socket.IO Backend for 3D Face Reconstruction
Handles real-time webcam streaming, model inference, and mesh transmission
Optimized for CPU performance with async processing
"""

from flask import Flask, jsonify
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import numpy as np
import yaml
import os
from threading import Lock
from concurrent.futures import ThreadPoolExecutor
import base64

# Import custom modules
from model_wrapper import FaceModel
from server_utils.preprocessor import FramePreprocessor
from server_utils.face_detector import FaceDetector
from server_utils.logger import PerformanceLogger


# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key-here'

# Enable CORS
CORS(app, resources={r"/*": {"origins": "*"}})

# Load configuration
with open('config.yaml', 'r') as f:
    config = yaml.safe_load(f)

# Initialize Socket.IO with optimizations
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',  # Use threading for CPU-bound tasks
    ping_timeout=config['socket']['ping_timeout'],
    ping_interval=config['socket']['ping_interval'],
    max_http_buffer_size=config['socket']['max_message_size']
)

# Global components
face_model = None
preprocessor = None
face_detector = None
perf_logger = None
thread_pool = None
processing_lock = Lock()

# Frame processing state
frame_counter = 0
last_face_bbox = None


def initialize_components():
    """Initialize all model components"""
    global face_model, preprocessor, face_detector, perf_logger, thread_pool
    
    print("[Server] Initializing components...")
    
    # Initialize performance logger
    perf_logger = PerformanceLogger(
        window_size=30,
        log_interval=config['logging']['log_interval'],
        verbose=config['logging']['verbose']
    )
    
    # Initialize preprocessor
    preprocessor = FramePreprocessor(
        target_size=config['performance']['input_resolution'],
        normalize=True
    )
    
    # Initialize face detector
    face_detector = FaceDetector(
        device=config['model']['device'],
        min_confidence=config['face_detection']['min_confidence']
    )
    
    # Initialize 3DDFA_V2 model
    face_model = FaceModel(config_path='config.yaml')
    
    # Initialize thread pool for async processing
    thread_pool = ThreadPoolExecutor(
        max_workers=config['performance']['thread_pool_size']
    )
    
    print("[Server] All components initialized successfully")
    print(f"[Server] Running on {config['model']['device'].upper()} mode")
    print(f"[Server] Expected FPS: {config['performance']['max_fps']}")


@app.route('/')
def index():
    """Health check endpoint"""
    return jsonify({
        'status': 'running',
        'model_info': face_model.get_info() if face_model else {},
        'config': {
            'device': config['model']['device'],
            'resolution': config['performance']['input_resolution'],
            'max_fps': config['performance']['max_fps']
        }
    })


@app.route('/health')
def health():
    """Detailed health check"""
    return jsonify({
        'status': 'healthy',
        'components': {
            'model': face_model is not None and face_model.is_loaded,
            'preprocessor': preprocessor is not None,
            'face_detector': face_detector is not None,
            'performance_logger': perf_logger is not None
        },
        'metrics': perf_logger.get_current_metrics() if perf_logger else {}
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print(f"[Socket] Client connected")
    emit('connected', {
        'message': 'Connected to 3D Face Reconstruction server',
        'device': config['model']['device'],
        'resolution': config['performance']['input_resolution']
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print(f"[Socket] Client disconnected")
    
    # Reset tracking state
    if face_detector:
        face_detector.reset_tracking()


@socketio.on('frame')
def handle_frame(data):
    """
    Handle incoming webcam frame from client
    
    Args:
        data: Dictionary containing frame data (base64 or binary)
    """
    global frame_counter, last_face_bbox
    
    # Start performance measurement
    perf_logger.start_frame()
    
    try:
        # Frame skipping for performance
        frame_skip = config['performance']['frame_skip']
        frame_counter += 1
        
        if frame_counter % frame_skip != 0:
            # Skip this frame
            perf_logger.end_frame(success=False)
            return
            
        # Decode frame
        if isinstance(data, dict) and 'image' in data:
            frame = preprocessor.decode_frame(data['image'])
        elif isinstance(data, bytes):
            frame = preprocessor.decode_binary_frame(data)
        else:
            print("[Server] Invalid frame data format")
            perf_logger.end_frame(success=False)
            return
            
        if frame is None:
            print("[Server] Failed to decode frame")
            perf_logger.end_frame(success=False)
            emit('error', {'message': 'Failed to decode frame'})
            return
            
        # Process frame asynchronously
        thread_pool.submit(process_frame, frame)
        
    except Exception as e:
        print(f"[Server] Error handling frame: {e}")
        perf_logger.end_frame(success=False)
        emit('error', {'message': str(e)})


def process_frame(frame: np.ndarray):
    """
    Process frame and emit 3D mesh result
    
    Args:
        frame: Decoded frame (RGB format)
    """
    global last_face_bbox
    
    try:
        # Detect face
        enable_tracking = config['performance']['enable_tracking']
        redetect_interval = config['performance']['redetect_interval']
        
        # Force redetection periodically
        if enable_tracking and face_detector.should_redetect(redetect_interval):
            face_detector.reset_tracking()
            
        bbox = face_detector.detect_face(frame, use_tracking=enable_tracking)
        
        if bbox is None:
            # No face detected
            socketio.emit('no_face', {'message': 'No face detected'})
            perf_logger.end_frame(success=False)
            return
            
        last_face_bbox = bbox
        
        # Extract face ROI
        face_roi = face_detector.extract_face_roi(
            frame,
            bbox,
            target_size=config['performance']['input_resolution']
        )
        
        if face_roi is None:
            socketio.emit('no_face', {'message': 'Failed to extract face'})
            perf_logger.end_frame(success=False)
            return
            
        # Run 3DDFA_V2 inference with original frame and bbox
        # Note: 3DDFA_V2 expects the full frame and bbox, not the cropped ROI
        mesh_data = face_model.predict(frame, bbox)
        
        if mesh_data is None:
            socketio.emit('error', {'message': 'Model inference failed'})
            perf_logger.end_frame(success=False)
            return
            
        # Get current performance metrics
        metrics = perf_logger.get_current_metrics()
        
        # Emit mesh data to client
        if config['socket']['binary_format']:
            # Send as binary for efficiency (optional - implement custom serialization)
            socketio.emit('mesh_update', {
                'vertices': mesh_data['vertices'],
                'faces': mesh_data['faces'],
                'metrics': metrics,
                'face_detected': True
            })
        else:
            # Send as JSON
            socketio.emit('mesh_update', {
                'vertices': mesh_data['vertices'],
                'faces': mesh_data['faces'],
                'metrics': metrics,
                'face_detected': True
            })
            
        # Mark frame processing complete
        perf_logger.end_frame(success=True)
        
    except Exception as e:
        print(f"[Server] Error processing frame: {e}")
        socketio.emit('error', {'message': f'Processing error: {str(e)}'})
        perf_logger.end_frame(success=False)


@socketio.on('get_metrics')
def handle_get_metrics():
    """Send current performance metrics to client"""
    if perf_logger:
        metrics = perf_logger.get_current_metrics()
        emit('metrics_update', metrics)


@socketio.on('reset_metrics')
def handle_reset_metrics():
    """Reset performance metrics"""
    if perf_logger:
        perf_logger.reset()
        emit('metrics_reset', {'message': 'Metrics reset successfully'})


@socketio.on('recalibrate')
def handle_recalibrate():
    """Reset face detection/tracking"""
    global last_face_bbox
    
    if face_detector:
        face_detector.reset_tracking()
        last_face_bbox = None
        emit('recalibrated', {'message': 'Face tracking reset'})


if __name__ == '__main__':
    # Initialize all components
    initialize_components()
    
    # Print startup information
    print("\n" + "="*60)
    print("3D FACE RECONSTRUCTION SERVER")
    print("="*60)
    print(f"Device: {config['model']['device'].upper()}")
    print(f"Resolution: {config['performance']['input_resolution']}x{config['performance']['input_resolution']}")
    print(f"Frame Skip: {config['performance']['frame_skip']}")
    print(f"Max FPS: {config['performance']['max_fps']}")
    print(f"ONNX Runtime: {'Enabled' if config['model']['use_onnx'] else 'Disabled'}")
    print("="*60)
    print(f"Server running on http://{config['server']['host']}:{config['server']['port']}")
    print("Waiting for client connections...")
    print("="*60 + "\n")
    
    # Run server
    socketio.run(
        app,
        host=config['server']['host'],
        port=config['server']['port'],
        debug=config['server']['debug'],
        use_reloader=False  # Disable reloader to prevent double initialization
    )
