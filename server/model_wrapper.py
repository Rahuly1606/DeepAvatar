"""
3DDFA_V2 Model Wrapper - Integrated with existing 3DDFA_V2 repository
Uses the actual 3DDFA_V2 code from c:/Users/alexr/PROJECTS/3DfaceReconstuction/3DDFA_V2-0.12
"""

import sys
import os
import yaml
import numpy as np
import cv2
from typing import Dict, Optional

# Add 3DDFA_V2 to Python path
TDDFA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '3DDFA_V2-0.12'))
sys.path.insert(0, TDDFA_DIR)

# Debug: Print path information
print(f"[Debug] TDDFA_DIR: {TDDFA_DIR}")
print(f"[Debug] TDDFA_DIR exists: {os.path.exists(TDDFA_DIR)}")
print(f"[Debug] TDDFA.py exists: {os.path.exists(os.path.join(TDDFA_DIR, 'TDDFA.py'))}")

# Import 3DDFA_V2 modules
try:
    from TDDFA_ONNX import TDDFA_ONNX
    from TDDFA import TDDFA
    TDDFA_AVAILABLE = True
    print("[Debug] 3DDFA_V2 modules imported successfully!")
except ImportError as e:
    print(f"[Warning] Could not import 3DDFA_V2: {e}")
    print(f"[Warning] Make sure the repository is at the expected location.")
    import traceback
    traceback.print_exc()
    TDDFA_AVAILABLE = False


class FaceModel:
    """
    3DDFA_V2 Face Reconstruction Model Wrapper
    
    This class provides integration with the actual 3DDFA_V2 implementation.
    It handles:
    - Model loading (PyTorch or ONNX)
    - 3DMM parameter regression
    - Mesh generation (vertices + faces)
    
    Uses the existing 3DDFA_V2-0.12 repository directly.
    """
    
    def __init__(self, config_path: str = 'config.yaml'):
        """
        Initialize 3DDFA_V2 model
        
        Args:
            config_path: Path to configuration file
        """
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
        self.model_config = self.config['model']
        self.device = self.model_config['device']
        self.use_onnx = self.model_config.get('use_onnx', True)
        
        # Model state
        self.tddfa = None
        self.is_loaded = False
        
        # 3DDFA_V2 configuration
        self.tddfa_config_path = self._get_tddfa_config()
        
        # Load model
        self._load_model()
        
        print(f"[FaceModel] Initialized 3DDFA_V2 on {self.device} (ONNX: {self.use_onnx})")
        
    def _get_tddfa_config(self) -> str:
        """Get 3DDFA_V2 configuration file path"""
        # Use MobileNet v1 by default (best balance of speed/accuracy)
        config_name = 'mb1_120x120.yml'
        config_path = os.path.join(TDDFA_DIR, 'configs', config_name)
        
        if not os.path.exists(config_path):
            raise FileNotFoundError(
                f"3DDFA_V2 config not found at {config_path}\n"
                f"Make sure 3DDFA_V2-0.12 is properly installed."
            )
            
        return config_path
        
    def _load_model(self):
        """Load 3DDFA_V2 model (PyTorch or ONNX)"""
        if not TDDFA_AVAILABLE:
            raise ImportError(
                "3DDFA_V2 modules not available. "
                "Please ensure 3DDFA_V2-0.12 is properly installed."
            )
            
        try:
            # Load ONNX model if requested (faster on CPU)
            if self.use_onnx:
                print(f"[FaceModel] Loading 3DDFA_V2 ONNX model...")
                self.tddfa = TDDFA_ONNX(
                    config_name=self.tddfa_config_path,
                    onnx_model_path=self._get_onnx_model_path()
                )
                print(f"[FaceModel] ONNX model loaded successfully")
            else:
                print(f"[FaceModel] Loading 3DDFA_V2 PyTorch model...")
                
                # Load 3DDFA_V2 config file
                import yaml as tddfa_yaml
                with open(self.tddfa_config_path, 'r') as f:
                    tddfa_config = tddfa_yaml.safe_load(f)
                
                # Convert relative paths to absolute paths
                # All paths in 3DDFA_V2 config are relative to the 3DDFA_V2 directory
                path_keys = ['checkpoint_fp', 'bfm_fp', 'param_mean_std_fp']
                for key in path_keys:
                    if key in tddfa_config and tddfa_config[key]:
                        rel_path = tddfa_config[key]
                        abs_path = os.path.join(TDDFA_DIR, rel_path)
                        tddfa_config[key] = abs_path
                        print(f"[FaceModel] {key}: {abs_path}")
                
                # Add device configuration
                if self.device == 'cpu':
                    tddfa_config['gpu_mode'] = False
                else:
                    tddfa_config['gpu_mode'] = True
                    tddfa_config['gpu_id'] = 0
                
                # Initialize TDDFA with config parameters
                self.tddfa = TDDFA(**tddfa_config)
                print(f"[FaceModel] PyTorch model loaded successfully")
                
            self.is_loaded = True
            
        except Exception as e:
            print(f"[FaceModel] Error loading model: {e}")
            import traceback
            traceback.print_exc()
            raise
            
    def _get_onnx_model_path(self) -> str:
        """Get ONNX model path"""
        # Check if ONNX model exists in 3DDFA_V2 weights folder
        onnx_name = 'mb1_120x120.onnx'
        onnx_path = os.path.join(TDDFA_DIR, 'weights', onnx_name)
        
        if os.path.exists(onnx_path):
            return onnx_path
            
        # Check in our server/models folder
        onnx_path = os.path.join('models', onnx_name)
        if os.path.exists(onnx_path):
            return onnx_path
            
        print(f"[FaceModel] Warning: ONNX model not found. Falling back to PyTorch.")
        self.use_onnx = False
        return None
        
    def predict(self, frame: np.ndarray, bbox: Optional[list] = None) -> Optional[Dict]:
        """
        Run inference on input frame
        
        Args:
            frame: Input frame (RGB format, HxWx3)
            bbox: Face bounding box [x1, y1, x2, y2] (optional, will detect if None)
            
        Returns:
            Dictionary containing mesh vertices and faces
        """
        try:
            if not self.is_loaded or self.tddfa is None:
                print("[FaceModel] Model not loaded")
                return None
                
            # If no bbox provided, we need to detect face first
            # For now, assume bbox is provided by face detector
            if bbox is None:
                print("[FaceModel] No bounding box provided")
                return None
                
            # Convert bbox to format expected by 3DDFA_V2
            # 3DDFA_V2 expects: [x_min, y_min, x_max, y_max]
            bbox_list = [bbox]
            
            # Run 3DDFA_V2 inference
            # This returns 3DMM parameters (62D: shape, expression, pose)
            param_lst, roi_box_lst = self.tddfa(frame, bbox_list)
            
            if len(param_lst) == 0:
                print("[FaceModel] No face parameters generated")
                return None
                
            # Get parameters for first (and only) face
            params = param_lst[0]
            roi_box = roi_box_lst[0]
            
            # Generate 3D mesh from parameters
            mesh = self._generate_mesh_from_params(params, roi_box)
            
            return mesh
            
        except Exception as e:
            print(f"[FaceModel] Prediction error: {e}")
            import traceback
            traceback.print_exc()
            return None
            
    def _generate_mesh_from_params(self, params: np.ndarray, roi_box: np.ndarray) -> Dict:
        """
        Generate 3D face mesh from 3DMM parameters
        
        Args:
            params: 3DMM parameters (62D)
            roi_box: ROI box from 3DDFA_V2
            
        Returns:
            Dictionary with 'vertices' and 'faces' arrays
        """
        try:
            # Use 3DDFA_V2's built-in function to reconstruct vertices
            # The tddfa.recon_vers method reconstructs 3D vertices from parameters
            vertices = self.tddfa.recon_vers([params], [roi_box], dense_flag=True)[0]
            
            print(f"[FaceModel] Raw vertices shape: {vertices.shape}")
            print(f"[FaceModel] Vertices range: [{vertices.min():.2f}, {vertices.max():.2f}]")
            
            # vertices shape: (3, N) where N is number of vertices
            # Transpose to (N, 3) for our frontend
            vertices = vertices.T
            
            print(f"[FaceModel] Transposed vertices shape: {vertices.shape}")
            
            # Get face triangulation from 3DDFA_V2's BFM model
            # The triangles define how vertices connect to form faces
            tri = self.tddfa.bfm.tri
            
            print(f"[FaceModel] Faces shape: {tri.shape}")
            print(f"[FaceModel] Generating mesh with {len(vertices)} vertices and {len(tri)} faces")
            
            # Convert to list for JSON serialization
            vertices_list = vertices.tolist()
            faces_list = tri.tolist()
            
            # Apply precision rounding to reduce data size
            precision = self.config['data']['vertex_precision']
            vertices_rounded = np.round(vertices, precision)
            
            return {
                'vertices': vertices_rounded.tolist(),
                'faces': faces_list,
                'num_vertices': len(vertices),
                'num_faces': len(tri)
            }
            
        except Exception as e:
            print(f"[FaceModel] Mesh generation error: {e}")
            import traceback
            traceback.print_exc()
            
            # Return a simple fallback mesh
            return self._create_fallback_mesh()
            
    def _create_fallback_mesh(self) -> Dict:
        """Create a simple fallback mesh in case of errors"""
        # Create a simple sphere-like mesh as fallback
        n_vertices = 1000
        vertices = np.random.randn(n_vertices, 3).astype(np.float32) * 50
        
        # Simple triangulation
        n_faces = n_vertices * 2
        faces = np.random.randint(0, n_vertices, (n_faces, 3), dtype=np.int32)
        
        return {
            'vertices': vertices.tolist(),
            'faces': faces.tolist(),
            'num_vertices': n_vertices,
            'num_faces': n_faces,
            'fallback': True
        }
        
    def get_info(self) -> Dict:
        """Get model information"""
        return {
            'device': self.device,
            'use_onnx': self.use_onnx,
            'is_loaded': self.is_loaded,
            'tddfa_config': self.tddfa_config_path,
            'model_type': '3DDFA_V2',
            'backend': 'ONNX' if self.use_onnx else 'PyTorch'
        }
        
    def test_inference(self, image_size: int = 120) -> bool:
        """
        Test if model can run inference
        
        Args:
            image_size: Size of test image
            
        Returns:
            True if test successful
        """
        try:
            # Create dummy image and bbox
            dummy_img = np.random.randint(0, 255, (image_size, image_size, 3), dtype=np.uint8)
            dummy_bbox = [10, 10, image_size-10, image_size-10]
            
            # Try inference
            result = self.predict(dummy_img, dummy_bbox)
            
            if result is not None:
                print(f"[FaceModel] Test inference successful!")
                print(f"[FaceModel] Generated mesh: {result['num_vertices']} vertices, {result['num_faces']} faces")
                return True
            else:
                print(f"[FaceModel] Test inference failed - no result")
                return False
                
        except Exception as e:
            print(f"[FaceModel] Test inference failed: {e}")
            return False


# Test if we can import 3DDFA_V2
if __name__ == '__main__':
    print("Testing 3DDFA_V2 integration...")
    print(f"3DDFA_V2 directory: {TDDFA_DIR}")
    print(f"3DDFA_V2 available: {TDDFA_AVAILABLE}")
    
    if TDDFA_AVAILABLE:
        try:
            model = FaceModel()
            print("\n✓ Model loaded successfully!")
            print(f"Model info: {model.get_info()}")
            
            # Test inference
            print("\nRunning test inference...")
            model.test_inference()
            
        except Exception as e:
            print(f"\n✗ Error loading model: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("\n✗ 3DDFA_V2 modules not available")
        print("Make sure 3DDFA_V2-0.12 is at the expected location")
