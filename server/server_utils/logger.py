"""
Performance Logger for 3D Face Reconstruction
Tracks and logs FPS, latency, and system resource usage
"""

import time
import psutil
import logging
from collections import deque
from typing import Dict, Optional
import numpy as np


class PerformanceLogger:
    """
    Monitors and logs real-time performance metrics
    - FPS (frames per second)
    - Latency (processing time per frame)
    - CPU/Memory usage
    - Frame drop statistics
    """
    
    def __init__(self, window_size: int = 30, log_interval: int = 30, verbose: bool = False):
        """
        Initialize performance logger
        
        Args:
            window_size: Number of frames to average for FPS calculation
            log_interval: Log statistics every N frames
            verbose: Enable detailed logging
        """
        self.window_size = window_size
        self.log_interval = log_interval
        self.verbose = verbose
        
        # Performance metrics
        self.frame_times = deque(maxlen=window_size)
        self.processing_times = deque(maxlen=window_size)
        self.frame_count = 0
        self.dropped_frames = 0
        
        # Timing
        self.start_time = None
        self.last_frame_time = time.time()
        self.last_log_time = time.time()
        
        # Setup logging
        self._setup_logging()
        
    def _setup_logging(self):
        """Configure logging format"""
        logging.basicConfig(
            level=logging.DEBUG if self.verbose else logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
        self.logger = logging.getLogger(__name__)
        
    def start_frame(self) -> float:
        """
        Mark the start of frame processing
        
        Returns:
            Timestamp when frame processing started
        """
        self.start_time = time.time()
        return self.start_time
        
    def end_frame(self, success: bool = True):
        """
        Mark the end of frame processing and update metrics
        
        Args:
            success: Whether the frame was processed successfully
        """
        if self.start_time is None:
            return
            
        # Calculate processing time
        end_time = time.time()
        processing_time = (end_time - self.start_time) * 1000  # Convert to ms
        
        # Calculate frame interval
        frame_interval = (end_time - self.last_frame_time) * 1000
        
        # Update metrics
        if success:
            self.processing_times.append(processing_time)
            self.frame_times.append(frame_interval)
            self.frame_count += 1
        else:
            self.dropped_frames += 1
            
        self.last_frame_time = end_time
        
        # Log periodically
        if self.frame_count % self.log_interval == 0:
            self._log_metrics()
            
        self.start_time = None
        
    def _log_metrics(self):
        """Log current performance metrics"""
        current_time = time.time()
        elapsed = current_time - self.last_log_time
        
        if len(self.processing_times) == 0:
            return
            
        # Calculate metrics
        avg_processing = np.mean(self.processing_times)
        avg_fps = 1000.0 / np.mean(self.frame_times) if len(self.frame_times) > 0 else 0
        min_latency = np.min(self.processing_times)
        max_latency = np.max(self.processing_times)
        
        # System resources
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        
        # Log statistics
        self.logger.info(
            f"[Performance] Frames: {self.frame_count} | "
            f"FPS: {avg_fps:.2f} | "
            f"Latency: {avg_processing:.1f}ms (min: {min_latency:.1f}ms, max: {max_latency:.1f}ms) | "
            f"Dropped: {self.dropped_frames} | "
            f"CPU: {cpu_percent:.1f}% | "
            f"RAM: {memory.percent:.1f}%"
        )
        
        self.last_log_time = current_time
        
    def get_current_metrics(self) -> Dict[str, float]:
        """
        Get current performance metrics
        
        Returns:
            Dictionary containing FPS, latency, and resource usage
        """
        if len(self.processing_times) == 0:
            return {
                'fps': 0.0,
                'avg_latency': 0.0,
                'min_latency': 0.0,
                'max_latency': 0.0,
                'dropped_frames': self.dropped_frames,
                'cpu_percent': 0.0,
                'memory_percent': 0.0
            }
            
        avg_fps = 1000.0 / np.mean(self.frame_times) if len(self.frame_times) > 0 else 0
        
        cpu_percent = psutil.cpu_percent(interval=0)
        memory = psutil.virtual_memory()
        
        return {
            'fps': round(avg_fps, 2),
            'avg_latency': round(np.mean(self.processing_times), 1),
            'min_latency': round(np.min(self.processing_times), 1),
            'max_latency': round(np.max(self.processing_times), 1),
            'dropped_frames': self.dropped_frames,
            'cpu_percent': round(cpu_percent, 1),
            'memory_percent': round(memory.percent, 1)
        }
        
    def reset(self):
        """Reset all metrics"""
        self.frame_times.clear()
        self.processing_times.clear()
        self.frame_count = 0
        self.dropped_frames = 0
        self.last_frame_time = time.time()
        self.last_log_time = time.time()
        self.logger.info("Performance metrics reset")
