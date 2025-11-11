"""
Person detection module using YOLOv8
Handles model loading, inference, and result processing
"""

import cv2
import torch
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from app.utils import get_logger

logger = get_logger(__name__)


@dataclass
class Detection:
    """Represents a detected person"""
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_id: int
    class_name: str
    
    @property
    def center(self) -> Tuple[float, float]:
        """Get center point of detection"""
        return ((self.x1 + self.x2) / 2, (self.y1 + self.y2) / 2)
    
    @property
    def width(self) -> float:
        """Get width of bounding box"""
        return self.x2 - self.x1
    
    @property
    def height(self) -> float:
        """Get height of bounding box"""
        return self.y2 - self.y1
    
    @property
    def area(self) -> float:
        """Get area of bounding box"""
        return self.width * self.height


class PersonDetector:
    """
    Person detection using YOLOv8
    Supports GPU acceleration and configurable confidence thresholds
    """
    
    def __init__(
        self,
        model_path: str = "yolov8n.pt",
        confidence_threshold: float = 0.5,
        nms_threshold: float = 0.5,
        use_gpu: bool = True
    ):
        """
        Initialize person detector
        
        Args:
            model_path: Path to YOLOv8 model
            confidence_threshold: Minimum confidence for detections
            nms_threshold: NMS threshold for post-processing
            use_gpu: Use GPU for inference if available
        """
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.nms_threshold = nms_threshold
        self.use_gpu = use_gpu and torch.cuda.is_available()
        self.device = "cuda" if self.use_gpu else "cpu"
        
        logger.info(f"Loading YOLOv8 model from {model_path}")
        logger.info(f"Using device: {self.device}")
        
        try:
            from ultralytics import YOLO
            self.model = YOLO(model_path)
            self.model.to(self.device)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise
    
    def detect(self, frame: np.ndarray) -> List[Detection]:
        """
        Detect persons in frame
        
        Args:
            frame: Input frame (BGR format)
        
        Returns:
            List of Detection objects
        """
        try:
            # Run inference
            results = self.model(
                frame,
                conf=self.confidence_threshold,
                iou=self.nms_threshold,
                verbose=False
            )
            
            detections = []
            
            # Process results
            for result in results:
                if result.boxes is None:
                    continue
                
                for box in result.boxes:
                    # Only keep person class (class_id = 0 in COCO)
                    if int(box.cls) != 0:
                        continue
                    
                    x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                    confidence = float(box.conf[0].cpu().numpy())
                    
                    detection = Detection(
                        x1=float(x1),
                        y1=float(y1),
                        x2=float(x2),
                        y2=float(y2),
                        confidence=confidence,
                        class_id=0,
                        class_name="person"
                    )
                    detections.append(detection)
            
            return detections
        
        except Exception as e:
            logger.error(f"Detection error: {e}")
            return []
    
    def detect_batch(self, frames: List[np.ndarray]) -> List[List[Detection]]:
        """
        Detect persons in multiple frames
        
        Args:
            frames: List of input frames
        
        Returns:
            List of detection lists
        """
        return [self.detect(frame) for frame in frames]
    
    def get_model_info(self) -> dict:
        """Get model information"""
        return {
            "model_path": self.model_path,
            "device": self.device,
            "confidence_threshold": self.confidence_threshold,
            "nms_threshold": self.nms_threshold,
            "gpu_available": torch.cuda.is_available(),
            "gpu_name": torch.cuda.get_device_name(0) if torch.cuda.is_available() else None
        }
