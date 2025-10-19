"""
Dependency Checker Script
Verifies all required dependencies are installed correctly
"""

import sys
import subprocess

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    print("✓ Python version OK")
    return True


def check_package(package_name, import_name=None):
    """Check if a Python package is installed"""
    if import_name is None:
        import_name = package_name
    
    try:
        __import__(import_name)
        print(f"✓ {package_name} installed")
        return True
    except ImportError:
        print(f"❌ {package_name} not installed")
        return False


def check_node():
    """Check Node.js installation"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"Node.js version: {version}")
        print("✓ Node.js installed")
        return True
    except FileNotFoundError:
        print("❌ Node.js not installed")
        return False


def check_npm():
    """Check npm installation"""
    try:
        result = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        version = result.stdout.strip()
        print(f"npm version: {version}")
        print("✓ npm installed")
        return True
    except FileNotFoundError:
        print("❌ npm not installed")
        return False


def main():
    """Run all dependency checks"""
    print("="*60)
    print("3D Face Reconstruction - Dependency Checker")
    print("="*60)
    print()
    
    all_ok = True
    
    # Check Python
    print("Checking Python environment...")
    all_ok &= check_python_version()
    print()
    
    # Check Python packages
    print("Checking Python packages...")
    packages = [
        ('flask', 'flask'),
        ('flask-socketio', 'flask_socketio'),
        ('flask-cors', 'flask_cors'),
        ('torch', 'torch'),
        ('opencv-python', 'cv2'),
        ('numpy', 'numpy'),
        ('scipy', 'scipy'),
        ('pyyaml', 'yaml'),
        ('psutil', 'psutil'),
        ('facenet-pytorch', 'facenet_pytorch')
    ]
    
    for package, import_name in packages:
        all_ok &= check_package(package, import_name)
    
    print()
    
    # Check ONNX Runtime (optional)
    print("Checking optional packages...")
    check_package('onnxruntime', 'onnxruntime')
    print()
    
    # Check Node.js
    print("Checking Node.js environment...")
    all_ok &= check_node()
    all_ok &= check_npm()
    print()
    
    # Summary
    print("="*60)
    if all_ok:
        print("✓ All required dependencies are installed!")
        print()
        print("Next steps:")
        print("1. Download model weights to server/models/")
        print("2. Run: cd server && python app.py")
        print("3. Run: cd client && npm run dev")
        print("4. Open: http://localhost:5173")
    else:
        print("❌ Some dependencies are missing")
        print()
        print("To install missing Python packages:")
        print("  cd server")
        print("  pip install -r requirements.txt")
        print()
        print("To install missing Node.js packages:")
        print("  cd client")
        print("  npm install")
    
    print("="*60)


if __name__ == '__main__':
    main()
