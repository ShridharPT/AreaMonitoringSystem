"""
Multi-camera management system
Handles multiple camera inputs and frame synchronization
"""

import cv2
import threading
import queue
import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app.utils import get_logger

logger = get_logger(__name__)


@dataclass
class CameraFrame:
    """Represents a camera frame"""
    camera_id: str
    frame: any
    timestamp: float
    frame_number: int
    width: int
    height: int


class CameraThread(threading.Thread):
    """Thread for reading frames from a single camera"""
    
    def __init__(
        self,
        camera_id: str,
        camera_index: int,
        width: int = 640,
        height: int = 480,
        fps: int = 30,
        queue_size: int = 2
    ):
        """
        Initialize camera thread
        
        Args:
            camera_id: Unique camera identifier
            camera_index: OpenCV camera index
            width: Frame width
            height: Frame height
            fps: Target FPS
            queue_size: Frame queue size
        """
        super().__init__(daemon=True)
        
        self.camera_id = camera_id
        self.camera_index = camera_index
        self.width = width
        self.height = height
        self.fps = fps
        self.queue = queue.Queue(maxsize=queue_size)
        
        self.running = False
        self.frame_count = 0
        self.last_frame_time = 0
        
        # Open camera
        self.cap = cv2.VideoCapture(camera_index)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open camera {camera_index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        
        logger.info(f"Camera {camera_id} initialized (index: {camera_index})")
    
    def run(self) -> None:
        """Main thread loop"""
        self.running = True
        frame_delay = 1.0 / self.fps
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                
                if not ret:
                    logger.warning(f"Failed to read frame from camera {self.camera_id}")
                    continue
                
                # Create frame object
                camera_frame = CameraFrame(
                    camera_id=self.camera_id,
                    frame=frame,
                    timestamp=time.time(),
                    frame_number=self.frame_count,
                    width=frame.shape[1],
                    height=frame.shape[0]
                )
                
                # Put frame in queue (drop if full)
                try:
                    self.queue.put_nowait(camera_frame)
                except queue.Full:
                    pass
                
                self.frame_count += 1
                
                # Control frame rate
                time.sleep(frame_delay)
        
        except Exception as e:
            logger.error(f"Error in camera thread {self.camera_id}: {e}")
        finally:
            self.stop()
    
    def get_frame(self, timeout: float = 1.0) -> Optional[CameraFrame]:
        """
        Get the latest frame
        
        Args:
            timeout: Timeout in seconds
        
        Returns:
            CameraFrame or None if timeout
        """
        try:
            return self.queue.get(timeout=timeout)
        except queue.Empty:
            return None
    
    def stop(self) -> None:
        """Stop camera thread"""
        self.running = False
        if self.cap:
            self.cap.release()
        logger.info(f"Camera {self.camera_id} stopped")


class MultiCameraManager:
    """Manages multiple camera inputs"""
    
    def __init__(self):
        """Initialize multi-camera manager"""
        self.cameras: Dict[str, CameraThread] = {}
        self.latest_frames: Dict[str, Optional[CameraFrame]] = {}
        logger.info("Multi-camera manager initialized")
    
    def add_camera(
        self,
        camera_id: str,
        camera_index: int,
        width: int = 640,
        height: int = 480,
        fps: int = 30
    ) -> bool:
        """
        Add a camera
        
        Args:
            camera_id: Unique camera identifier
            camera_index: OpenCV camera index
            width: Frame width
            height: Frame height
            fps: Target FPS
        
        Returns:
            True if successful
        """
        try:
            if camera_id in self.cameras:
                logger.warning(f"Camera {camera_id} already exists")
                return False
            
            camera_thread = CameraThread(
                camera_id=camera_id,
                camera_index=camera_index,
                width=width,
                height=height,
                fps=fps
            )
            
            camera_thread.start()
            self.cameras[camera_id] = camera_thread
            self.latest_frames[camera_id] = None
            
            logger.info(f"Camera {camera_id} added and started")
            return True
        
        except Exception as e:
            logger.error(f"Failed to add camera {camera_id}: {e}")
            return False
    
    def remove_camera(self, camera_id: str) -> bool:
        """
        Remove a camera
        
        Args:
            camera_id: Camera identifier
        
        Returns:
            True if successful
        """
        if camera_id not in self.cameras:
            return False
        
        camera = self.cameras[camera_id]
        camera.stop()
        del self.cameras[camera_id]
        del self.latest_frames[camera_id]
        
        logger.info(f"Camera {camera_id} removed")
        return True
    
    def get_frame(self, camera_id: str) -> Optional[CameraFrame]:
        """
        Get latest frame from camera
        
        Args:
            camera_id: Camera identifier
        
        Returns:
            CameraFrame or None
        """
        if camera_id not in self.cameras:
            return None
        
        frame = self.cameras[camera_id].get_frame()
        if frame:
            self.latest_frames[camera_id] = frame
        
        return self.latest_frames[camera_id]
    
    def get_all_frames(self) -> Dict[str, Optional[CameraFrame]]:
        """Get latest frames from all cameras"""
        frames = {}
        for camera_id in self.cameras:
            frames[camera_id] = self.get_frame(camera_id)
        return frames
    
    def get_camera_ids(self) -> List[str]:
        """Get list of camera IDs"""
        return list(self.cameras.keys())
    
    def get_camera_count(self) -> int:
        """Get number of active cameras"""
        return len(self.cameras)
    
    def get_camera_info(self, camera_id: str) -> Optional[dict]:
        """Get camera information"""
        if camera_id not in self.cameras:
            return None
        
        camera = self.cameras[camera_id]
        return {
            "camera_id": camera_id,
            "frame_count": camera.frame_count,
            "fps": camera.fps,
            "width": camera.width,
            "height": camera.height,
            "running": camera.running
        }
    
    def get_all_camera_info(self) -> Dict[str, dict]:
        """Get information for all cameras"""
        info = {}
        for camera_id in self.cameras:
            info[camera_id] = self.get_camera_info(camera_id)
        return info
    
    def stop_all(self) -> None:
        """Stop all cameras"""
        for camera_id in list(self.cameras.keys()):
            self.remove_camera(camera_id)
        logger.info("All cameras stopped")
