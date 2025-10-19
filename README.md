# 3D Face Reconstruction - Real-Time Web App

A full-stack real-time 3D face reconstruction application using **3DDFA_V2** deep learning model, optimized for CPU performance.

## 🎯 Features

- **Real-time webcam streaming** with efficient frame processing
- **3DDFA_V2 model** running locally (no external APIs)
- **CPU-optimized** inference with ONNX Runtime and FP16 quantization
- **Interactive 3D visualization** with Three.js
- **Low-latency communication** using Socket.IO with binary data
- **Performance monitoring** (FPS counter, latency display)
- **UI controls** for lighting, mesh color, wireframe toggle
- **Frame skipping** mechanism for smooth performance

## 📋 Expected Performance

- **CPU Mode**: 2-8 FPS (depending on CPU capability)
- **Latency**: <200ms per frame on modern CPU
- **Resolution**: 256×256 or 320×320 (configurable)

## 🏗️ Project Structure

```
3DfaceReconstuction/
├── server/                    # Flask backend
│   ├── app.py                # Main Flask + Socket.IO server
│   ├── model_wrapper.py      # 3DDFA_V2 model interface
│   ├── utils/
│   │   ├── face_detector.py  # Lightweight face detection
│   │   ├── preprocessor.py   # Frame preprocessing utilities
│   │   └── logger.py         # Performance logging
│   ├── models/               # Model weights directory
│   ├── config.yaml           # Configuration file
│   └── requirements.txt      # Python dependencies
├── client/                   # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── WebcamStreamer.jsx
│   │   │   ├── MeshViewer.jsx
│   │   │   ├── ControlPanel.jsx
│   │   │   └── PerformanceMonitor.jsx
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── Dockerfile                # GPU-ready Docker setup
└── README.md
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8+
- Node.js 16+
- npm or yarn
- (Optional) NVIDIA GPU with CUDA 11.0+ for GPU acceleration

### 1. Download 3DDFA_V2 Model Weights

```bash
# Create models directory
mkdir -p server/models

# Download 3DDFA_V2 pretrained weights
# Visit: https://github.com/cleardusk/3DDFA_V2/releases
# Download the following files to server/models/:
# - phase1_wpdc_vdc.pth.tar
# - similarity_Lm3D_all.mat (landmark template)
```

### 2. Backend Setup (CPU-Optimized)

```bash
cd server

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Optional: Convert model to ONNX for faster CPU inference
python utils/convert_to_onnx.py
```

### 3. Frontend Setup

```bash
cd client

# Install dependencies
npm install

# Start development server
npm run dev
```

### 4. Run the Application

**Terminal 1 - Backend:**
```bash
cd server
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd client
npm run dev
```

Open browser at `http://localhost:5173`

## 🐳 Docker Setup (GPU-Ready)

```bash
# Build image
docker build -t 3d-face-recon .

# Run with GPU support
docker run --gpus all -p 5000:5000 -p 5173:5173 3d-face-recon

# Run CPU-only
docker run -p 5000:5000 -p 5173:5173 3d-face-recon
```

## ⚙️ Configuration

Edit `server/config.yaml`:

```yaml
model:
  weights_path: "./models/phase1_wpdc_vdc.pth.tar"
  device: "cpu"  # Change to "cuda" for GPU
  use_onnx: true  # Use ONNX Runtime for CPU optimization

performance:
  input_resolution: 256  # 256 or 320
  frame_skip: 2  # Process every Nth frame
  max_fps: 15
  
socket:
  compression: true
  binary_format: true

debug:
  log_performance: true
  verbose: false
```

## 🎮 UI Controls

- **Toggle Wireframe**: Switch between solid and wireframe mesh
- **Pause/Resume Stream**: Control webcam streaming
- **Lighting Controls**: Adjust ambient, directional, and point lights
- **Mesh Color**: Customize 3D face mesh color
- **Reset View**: Reset camera to default position

## 🔧 Switching to GPU Mode

To enable GPU acceleration (if NVIDIA GPU available):

1. Install CUDA-enabled PyTorch:
   ```bash
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118
   ```

2. Update `config.yaml`:
   ```yaml
   model:
     device: "cuda"
   ```

3. In `model_wrapper.py`, the code will automatically detect and use GPU.

Expected GPU performance: **15-30 FPS** with <50ms latency

## 🛠️ Troubleshooting

**Low FPS on CPU:**
- Increase `frame_skip` in config (try 3 or 4)
- Reduce `input_resolution` to 256
- Enable ONNX Runtime with `use_onnx: true`

**Socket Connection Errors:**
- Check firewall settings
- Ensure backend is running on port 5000
- Verify CORS settings in `app.py`

**Model Loading Errors:**
- Verify model weights are in `server/models/`
- Check file paths in `config.yaml`

## 📊 Performance Optimization Tips

1. **CPU Optimization**:
   - ONNX Runtime with FP16 quantization
   - Frame skipping (process every 2-3 frames)
   - Reduced input resolution (256×256)
   - Landmark tracking between frames

2. **Network Optimization**:
   - Binary data format (not JSON)
   - Frame compression
   - Adaptive frame rate based on latency

3. **Frontend Optimization**:
   - Canvas-based rendering
   - Three.js with minimal geometry updates
   - Debounced UI controls

## 📝 License

This project uses 3DDFA_V2 model. Please refer to the original repository for licensing:
https://github.com/cleardusk/3DDFA_V2

## 🙏 Acknowledgments

- [3DDFA_V2](https://github.com/cleardusk/3DDFA_V2) - 3D Dense Face Alignment
- Flask-SocketIO for real-time communication
- Three.js for 3D visualization
- React + Vite for frontend framework

---

**Note**: This application runs completely offline. No external APIs or cloud services are used.
