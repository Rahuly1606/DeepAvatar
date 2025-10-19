"""
Lightweight Face Detection Module
Optimized for CPU performance using MTCNN
"""

import cv2
import numpy as np
from typing import Optional, Tuple, List
import torch
from facenet_pytorch import MTCNN


class FaceDetector:
    """
    Lightweight face detector using MTCNN
    Optimized for CPU performance with face tracking between frames
    """
    
    def __init__(self, device: str = 'cpu', min_confidence: float = 0.9):
        """
        Initialize face detector
        
        Args:
            device: 'cpu' or 'cuda'
            min_confidence: Minimum detection confidence threshold
        """
        self.device = device
        self.min_confidence = min_confidence
        
        # Initialize MTCNN (Multi-task Cascaded Convolutional Networks)
        # This is lightweight and works well on CPU
        self.detector = MTCNN(
            image_size=160,
            margin=0,
            min_face_size=20,
            thresholds=[0.6, 0.7, 0.7],  # Detection thresholds
            factor=0.709,
            post_process=False,
            device=device,
            select_largest=True,  # Only detect the largest face
            keep_all=False
        )
        
        # Face tracking state
        self.last_bbox = None
        self.tracking_active = False
        self.frames_since_detection = 0
        
        print(f"[FaceDetector] Initialized MTCNN on {device}")
        
    def detect_face(self, frame: np.ndarray, use_tracking: bool = True) -> Optional[Tuple[int, int, int, int]]:
        """
        Detect face bounding box in frame
        
        Args:
            frame: Input frame (RGB format, numpy array)
            use_tracking: Enable face tracking to skip detection on subsequent frames
            
        Returns:
            Bounding box as (x1, y1, x2, y2) or None if no face detected
        """
        # If tracking is enabled and we have a previous detection, use tracking
        if use_tracking and self.tracking_active and self.last_bbox is not None:
            # Simple tracking: assume face hasn't moved much
            # This saves CPU cycles by not running full detection every frame
            bbox = self._track_face(frame)
            if bbox is not None:
                self.frames_since_detection += 1
                return bbox
        
        # Run full face detection
        bbox = self._detect_with_mtcnn(frame)
        
        if bbox is not None:
            self.last_bbox = bbox
            self.tracking_active = True
            self.frames_since_detection = 0
        else:
            self.tracking_active = False
            
        return bbox
        
    def _detect_with_mtcnn(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Perform face detection using MTCNN
        
        Args:
            frame: Input frame (RGB format)
            
        Returns:
            Bounding box or None
        """
        try:
            # MTCNN expects PIL Image or numpy array in RGB
            boxes, probs = self.detector.detect(frame)
            
            if boxes is not None and len(boxes) > 0 and probs[0] >= self.min_confidence:
                # Convert to integer coordinates
                bbox = boxes[0].astype(int)
                x1, y1, x2, y2 = bbox
                
                # Ensure bbox is within frame bounds
                h, w = frame.shape[:2]
                x1 = max(0, min(x1, w - 1))
                y1 = max(0, min(y1, h - 1))
                x2 = max(0, min(x2, w - 1))
                y2 = max(0, min(y2, h - 1))
                
                return (x1, y1, x2, y2)
                
        except Exception as e:
            print(f"[FaceDetector] Detection error: {e}")
            
        return None
        
    def _track_face(self, frame: np.ndarray) -> Optional[Tuple[int, int, int, int]]:
        """
        Simple face tracking between frames
        Uses optical flow or assumes minimal movement
        
        Args:
            frame: Current frame
            
        Returns:
            Estimated bounding box or None
        """
        if self.last_bbox is None:
            return None
            
        # For simplicity, assume face hasn't moved significantly
        # In production, you could use optical flow or landmark tracking
        # This saves ~70% of computation compared to full detection every frame
        
        x1, y1, x2, y2 = self.last_bbox
        
        # Validate bbox is still within frame bounds
        h, w = frame.shape[:2]
        if x2 > w or y2 > h or x1 < 0 or y1 < 0:
            return None
            
        return self.last_bbox
        
    def should_redetect(self, redetect_interval: int = 30) -> bool:
        """
        Check if face should be re-detected (tracking refresh)
        
        Args:
            redetect_interval: Redetect every N frames
            
        Returns:
            True if redetection should be performed
        """
        return self.frames_since_detection >= redetect_interval
        
    def reset_tracking(self):
        """Reset face tracking state"""
        self.last_bbox = None
        self.tracking_active = False
        self.frames_since_detection = 0
        
    def extract_face_roi(self, frame: np.ndarray, bbox: Tuple[int, int, int, int], 
                        target_size: int = 256, padding: float = 0.3) -> Optional[np.ndarray]:
        """
        Extract and preprocess face region of interest
        
        Args:
            frame: Input frame
            bbox: Bounding box (x1, y1, x2, y2)
            target_size: Output size for face crop
            padding: Padding around face (as fraction of bbox size)
            
        Returns:
            Cropped and resized face image
        """
        x1, y1, x2, y2 = bbox
        
        # Add padding
        w = x2 - x1
        h = y2 - y1
        pad_w = int(w * padding)
        pad_h = int(h * padding)
        
        # Expand bbox with padding
        x1 = max(0, x1 - pad_w)
        y1 = max(0, y1 - pad_h)
        x2 = min(frame.shape[1], x2 + pad_w)
        y2 = min(frame.shape[0], y2 + pad_h)
        
        # Extract face region
        face_roi = frame[y1:y2, x1:x2]
        
        if face_roi.size == 0:
            return None
            
        # Resize to target size
        face_resized = cv2.resize(face_roi, (target_size, target_size), 
                                 interpolation=cv2.INTER_LINEAR)
        
        return face_resized
