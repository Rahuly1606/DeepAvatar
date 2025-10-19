"""
Quick Setup Script for 3D Face Reconstruction
Integrates with existing 3DDFA_V2 repository
"""

import os
import shutil
import sys

# Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
TDDFA_PATH = os.path.join(PROJECT_ROOT, '3DDFA_V2-0.12')
SERVER_PATH = os.path.join(PROJECT_ROOT, 'server')
MODELS_PATH = os.path.join(SERVER_PATH, 'models')

def check_3ddfa_v2():
    """Check if 3DDFA_V2 repository exists"""
    print("\n" + "="*60)
    print("Checking 3DDFA_V2 Installation")
    print("="*60)
    
    if os.path.exists(TDDFA_PATH):
        print(f"✓ Found 3DDFA_V2 at: {TDDFA_PATH}")
        
        # Check for model weights
        weights_path = os.path.join(TDDFA_PATH, 'weights')
        if os.path.exists(weights_path):
            weights = os.listdir(weights_path)
            pth_files = [w for w in weights if w.endswith('.pth')]
            onnx_files = [w for w in weights if w.endswith('.onnx')]
            
            print(f"\nAvailable PyTorch models:")
            for pth in pth_files:
                size = os.path.getsize(os.path.join(weights_path, pth)) / (1024 * 1024)
                print(f"  ✓ {pth} ({size:.1f} MB)")
                
            print(f"\nAvailable ONNX models:")
            if onnx_files:
                for onnx in onnx_files:
                    size = os.path.getsize(os.path.join(weights_path, onnx)) / (1024 * 1024)
                    print(f"  ✓ {onnx} ({size:.1f} MB)")
            else:
                print("  ⚠ No ONNX models found")
                print("  → Download from: https://drive.google.com/file/d/1YpO1KfXvJHRmCBkErNa62dHm-CUjsoIk/view?usp=sharing")
                print("  → Save to: " + weights_path)
                
        return True
    else:
        print(f"✗ 3DDFA_V2 not found at: {TDDFA_PATH}")
        print("\nPlease clone 3DDFA_V2:")
        print("  git clone https://github.com/cleardusk/3DDFA_V2.git 3DDFA_V2-0.12")
        return False


def setup_model_integration():
    """Setup model integration"""
    print("\n" + "="*60)
    print("Setting Up Model Integration")
    print("="*60)
    
    # Create models directory if it doesn't exist
    os.makedirs(MODELS_PATH, exist_ok=True)
    print(f"✓ Models directory: {MODELS_PATH}")
    
    # Copy model wrapper
    src = os.path.join(SERVER_PATH, 'model_wrapper_3ddfa.py')
    dst = os.path.join(SERVER_PATH, 'model_wrapper.py')
    
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"✓ Updated model_wrapper.py to use 3DDFA_V2")
    else:
        print(f"⚠ model_wrapper_3ddfa.py not found")
        
    return True


def update_config():
    """Update configuration for 3DDFA_V2"""
    print("\n" + "="*60)
    print("Configuration")
    print("="*60)
    
    config_path = os.path.join(SERVER_PATH, 'config.yaml')
    
    print(f"\nConfiguration file: {config_path}")
    print("\nRecommended settings for CPU:")
    print("""
model:
  device: "cpu"
  use_onnx: true           # Use ONNX for 30% speed boost
  
performance:
  input_resolution: 256     # Lower resolution for faster processing
  frame_skip: 2             # Process every 2nd frame
  enable_tracking: true     # Save computation with face tracking
  max_fps: 15
  
face_detection:
  detector: "mtcnn"         # Lightweight face detector
  min_confidence: 0.9
""")
    
    print("\nFor GPU (if available):")
    print("""
model:
  device: "cuda"           # Enable GPU
  use_onnx: false          # PyTorch is fast enough on GPU
""")


def check_dependencies():
    """Check if required dependencies are installed"""
    print("\n" + "="*60)
    print("Checking Dependencies")
    print("="*60)
    
    dependencies = {
        'flask': 'Flask',
        'flask_socketio': 'Flask-SocketIO',
        'flask_cors': 'Flask-CORS',
        'cv2': 'OpenCV',
        'numpy': 'NumPy',
        'yaml': 'PyYAML',
        'torch': 'PyTorch',
    }
    
    missing = []
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✓ {name}")
        except ImportError:
            print(f"✗ {name}")
            missing.append(name)
            
    if missing:
        print(f"\n⚠ Missing dependencies: {', '.join(missing)}")
        print("\nInstall with:")
        print("  cd server")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("\n✓ All dependencies installed!")
        return True


def build_3ddfa_v2():
    """Build 3DDFA_V2 extensions"""
    print("\n" + "="*60)
    print("Building 3DDFA_V2 Extensions")
    print("="*60)
    
    build_script = os.path.join(TDDFA_PATH, 'build.sh')
    
    if os.path.exists(build_script):
        print(f"\nTo build 3DDFA_V2 extensions, run:")
        print(f"  cd {TDDFA_PATH}")
        print(f"  bash build.sh")
        print("\nThis will build:")
        print("  - FaceBoxes NMS (C++ extension)")
        print("  - Sim3DR (C++ rendering)")
        print("\n⚠ Note: This requires C++ compiler (Visual Studio on Windows)")
        print("If build fails, the app will work but without some optimizations.")
    else:
        print(f"⚠ Build script not found")
        
    return True


def test_setup():
    """Test the setup"""
    print("\n" + "="*60)
    print("Testing Setup")
    print("="*60)
    
    # Add paths
    sys.path.insert(0, SERVER_PATH)
    sys.path.insert(0, TDDFA_PATH)
    
    try:
        # Test import
        print("\nTesting model import...")
        from model_wrapper_3ddfa import FaceModel, TDDFA_AVAILABLE
        
        if not TDDFA_AVAILABLE:
            print("⚠ 3DDFA_V2 modules not available")
            print("  This might be because extensions are not built.")
            print("  Try building with: cd 3DDFA_V2-0.12 && bash build.sh")
            return False
            
        print("✓ Model wrapper imported successfully")
        
        # Test model loading
        print("\nTesting model loading...")
        config_path = os.path.join(SERVER_PATH, 'config.yaml')
        model = FaceModel(config_path)
        
        print("✓ Model loaded successfully!")
        print(f"\nModel info:")
        info = model.get_info()
        for key, value in info.items():
            print(f"  {key}: {value}")
            
        return True
        
    except Exception as e:
        print(f"✗ Setup test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run complete setup"""
    print("\n" + "="*70)
    print("3D FACE RECONSTRUCTION - QUICK SETUP")
    print("="*70)
    
    # Step 1: Check 3DDFA_V2
    if not check_3ddfa_v2():
        return
        
    # Step 2: Setup integration
    setup_model_integration()
    
    # Step 3: Check dependencies
    deps_ok = check_dependencies()
    
    # Step 4: Build instructions
    build_3ddfa_v2()
    
    # Step 5: Config
    update_config()
    
    # Step 6: Test
    if deps_ok:
        test_setup()
    
    # Final instructions
    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("""
1. Install dependencies (if not done):
   cd server
   pip install -r requirements.txt

2. (Optional) Build 3DDFA_V2 extensions:
   cd 3DDFA_V2-0.12
   bash build.sh
   
3. (Optional) Download ONNX model for best CPU performance:
   Download from: https://drive.google.com/file/d/1YpO1KfXvJHRmCBkErNa62dHm-CUjsoIk/view
   Save to: 3DDFA_V2-0.12/weights/mb1_120x120.onnx

4. Start the backend:
   cd server
   python app.py

5. Start the frontend:
   cd client
   npm install  # (first time only)
   npm run dev

6. Open browser:
   http://localhost:5173

""")
    print("="*70)


if __name__ == '__main__':
    main()
