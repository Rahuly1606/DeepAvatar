"""
Frame Preprocessing Utilities
Handles image conversion, resizing, normalization for model input
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import base64
from io import BytesIO
from PIL import Image


class FramePreprocessor:
    """
    Preprocesses webcam frames for 3DDFA_V2 model
    Handles decoding, resizing, normalization, and format conversion
    """
    
    def __init__(self, target_size: int = 256, normalize: bool = True):
        """
        Initialize frame preprocessor
        
        Args:
            target_size: Target resolution for model input (256 or 320)
            normalize: Apply ImageNet normalization
        """
        self.target_size = target_size
        self.normalize = normalize
        
        # ImageNet normalization constants (used by most pretrained models)
        self.mean = np.array([0.485, 0.456, 0.406], dtype=np.float32)
        self.std = np.array([0.229, 0.224, 0.225], dtype=np.float32)
        
    def decode_frame(self, frame_data: str) -> Optional[np.ndarray]:
        """
        Decode base64-encoded frame data to numpy array
        
        Args:
            frame_data: Base64-encoded image string
            
        Returns:
            Decoded frame as numpy array (RGB format) or None
        """
        try:
            # Remove data URL prefix if present
            if 'base64,' in frame_data:
                frame_data = frame_data.split('base64,')[1]
                
            # Decode base64
            img_bytes = base64.b64decode(frame_data)
            
            # Convert to numpy array
            img = Image.open(BytesIO(img_bytes))
            frame = np.array(img)
            
            # Convert to RGB if needed
            if len(frame.shape) == 2:  # Grayscale
                frame = cv2.cvtColor(frame, cv2.COLOR_GRAY2RGB)
            elif frame.shape[2] == 4:  # RGBA
                frame = cv2.cvtColor(frame, cv2.COLOR_RGBA2RGB)
                
            return frame
            
        except Exception as e:
            print(f"[Preprocessor] Frame decode error: {e}")
            return None
            
    def decode_binary_frame(self, frame_bytes: bytes) -> Optional[np.ndarray]:
        """
        Decode binary frame data to numpy array
        
        Args:
            frame_bytes: Raw image bytes
            
        Returns:
            Decoded frame as numpy array (RGB format) or None
        """
        try:
            # Decode using OpenCV
            nparr = np.frombuffer(frame_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return None
                
            # Convert BGR to RGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            return frame
            
        except Exception as e:
            print(f"[Preprocessor] Binary frame decode error: {e}")
            return None
            
    def resize_frame(self, frame: np.ndarray, target_size: Optional[int] = None) -> np.ndarray:
        """
        Resize frame to target size while maintaining aspect ratio
        
        Args:
            frame: Input frame
            target_size: Target size (uses self.target_size if None)
            
        Returns:
            Resized frame
        """
        if target_size is None:
            target_size = self.target_size
            
        h, w = frame.shape[:2]
        
        # Calculate aspect ratio preserving dimensions
        if h > w:
            new_h = target_size
            new_w = int(w * (target_size / h))
        else:
            new_w = target_size
            new_h = int(h * (target_size / w))
            
        # Resize
        resized = cv2.resize(frame, (new_w, new_h), interpolation=cv2.INTER_LINEAR)
        
        # Pad to square if needed
        if new_h != target_size or new_w != target_size:
            # Create black canvas
            canvas = np.zeros((target_size, target_size, 3), dtype=np.uint8)
            
            # Calculate padding
            pad_h = (target_size - new_h) // 2
            pad_w = (target_size - new_w) // 2
            
            # Place resized image on canvas
            canvas[pad_h:pad_h+new_h, pad_w:pad_w+new_w] = resized
            resized = canvas
            
        return resized
        
    def normalize_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Normalize frame using ImageNet statistics
        
        Args:
            frame: Input frame (RGB, 0-255)
            
        Returns:
            Normalized frame (RGB, mean-centered)
        """
        # Convert to float and scale to [0, 1]
        frame_float = frame.astype(np.float32) / 255.0
        
        # Apply ImageNet normalization
        frame_normalized = (frame_float - self.mean) / self.std
        
        return frame_normalized
        
    def prepare_model_input(self, frame: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Complete preprocessing pipeline for model input
        
        Args:
            frame: Input frame (RGB format)
            
        Returns:
            Tuple of (preprocessed_frame, original_resized) for model input and visualization
        """
        # Resize frame
        resized = self.resize_frame(frame)
        
        # Keep copy for visualization
        original_resized = resized.copy()
        
        # Normalize if enabled
        if self.normalize:
            preprocessed = self.normalize_frame(resized)
        else:
            preprocessed = resized.astype(np.float32) / 255.0
            
        # Convert to CHW format (channels first) for PyTorch
        preprocessed = np.transpose(preprocessed, (2, 0, 1))
        
        # Add batch dimension
        preprocessed = np.expand_dims(preprocessed, axis=0)
        
        return preprocessed, original_resized
        
    def denormalize_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Reverse normalization for visualization
        
        Args:
            frame: Normalized frame
            
        Returns:
            Denormalized frame (RGB, 0-255)
        """
        # Reverse normalization
        frame = (frame * self.std) + self.mean
        
        # Clip and convert to uint8
        frame = np.clip(frame * 255.0, 0, 255).astype(np.uint8)
        
        return frame
        
    def compress_for_transmission(self, data: np.ndarray, quality: int = 85) -> bytes:
        """
        Compress numpy array for efficient network transmission
        
        Args:
            data: Numpy array to compress
            quality: JPEG quality (1-100)
            
        Returns:
            Compressed bytes
        """
        # For image data
        if len(data.shape) == 3:
            _, buffer = cv2.imencode('.jpg', 
                                    cv2.cvtColor(data, cv2.COLOR_RGB2BGR),
                                    [cv2.IMWRITE_JPEG_QUALITY, quality])
            return buffer.tobytes()
            
        # For other data (mesh vertices, etc.)
        return data.astype(np.float32).tobytes()
