"""
Object tracking module
Tracks detected persons across frames using centroid tracking
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from datetime import datetime
from app.utils import get_logger

logger = get_logger(__name__)


@dataclass
class TrackedObject:
    """Represents a tracked object"""
    track_id: int
    class_name: str
    centroid: Tuple[float, float]
    bbox: Tuple[float, float, float, float]  # x1, y1, x2, y2
    confidence: float
    frames_seen: int = 1
    frames_since_seen: int = 0
    first_seen: datetime = field(default_factory=datetime.now)
    last_seen: datetime = field(default_factory=datetime.now)
    
    @property
    def age(self) -> int:
        """Get age of track in frames"""
        return self.frames_seen
    
    @property
    def is_stale(self) -> bool:
        """Check if track is stale (not seen recently)"""
        return self.frames_since_seen > 30


class CentroidTracker:
    """
    Simple centroid-based object tracker
    Tracks objects by matching centroids across frames
    """
    
    def __init__(
        self,
        max_disappeared: int = 30,
        max_distance: float = 50.0
    ):
        """
        Initialize centroid tracker
        
        Args:
            max_disappeared: Max frames object can disappear before removal
            max_distance: Max distance for centroid matching
        """
        self.max_disappeared = max_disappeared
        self.max_distance = max_distance
        
        self.next_object_id = 0
        self.objects: Dict[int, TrackedObject] = {}
        self.disappeared: Dict[int, int] = {}
        
        logger.info("Centroid tracker initialized")
    
    def update(self, detections: List) -> Dict[int, TrackedObject]:
        """
        Update tracker with new detections
        
        Args:
            detections: List of Detection objects
        
        Returns:
            Dictionary of tracked objects
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            
            return self.objects
        
        # Get centroids from detections
        input_centroids = np.array([d.center for d in detections])
        
        # If no tracked objects, register all detections
        if len(self.objects) == 0:
            for i, detection in enumerate(detections):
                self._register(detection)
        else:
            # Match detections to tracked objects
            object_ids = list(self.objects.keys())
            object_centroids = np.array([self.objects[oid].centroid for oid in object_ids])
            
            # Compute distances between centroids
            distances = self._compute_distances(object_centroids, input_centroids)
            
            # Find matches
            rows = distances.min(axis=1).argsort()
            cols = distances.argmin(axis=1)[rows]
            
            used_rows = set()
            used_cols = set()
            
            for row, col in zip(rows, cols):
                if distances[row, col] > self.max_distance:
                    continue
                
                if row in used_rows or col in used_cols:
                    continue
                
                object_id = object_ids[row]
                self._update(object_id, detections[col])
                
                used_rows.add(row)
                used_cols.add(col)
            
            # Handle unmatched object IDs
            unused_object_ids = set(range(len(object_ids))) - used_rows
            for row in unused_object_ids:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                
                if self.disappeared[object_id] > self.max_disappeared:
                    self._deregister(object_id)
            
            # Handle unmatched detections
            unused_detection_ids = set(range(len(detections))) - used_cols
            for col in unused_detection_ids:
                self._register(detections[col])
        
        return self.objects
    
    def _register(self, detection) -> None:
        """Register a new detection"""
        self.objects[self.next_object_id] = TrackedObject(
            track_id=self.next_object_id,
            class_name=detection.class_name,
            centroid=detection.center,
            bbox=(detection.x1, detection.y1, detection.x2, detection.y2),
            confidence=detection.confidence
        )
        self.disappeared[self.next_object_id] = 0
        self.next_object_id += 1
    
    def _update(self, object_id: int, detection) -> None:
        """Update existing track"""
        obj = self.objects[object_id]
        obj.centroid = detection.center
        obj.bbox = (detection.x1, detection.y1, detection.x2, detection.y2)
        obj.confidence = detection.confidence
        obj.frames_seen += 1
        obj.frames_since_seen = 0
        obj.last_seen = datetime.now()
        self.disappeared[object_id] = 0
    
    def _deregister(self, object_id: int) -> None:
        """Deregister a track"""
        del self.objects[object_id]
        del self.disappeared[object_id]
    
    @staticmethod
    def _compute_distances(
        object_centroids: np.ndarray,
        input_centroids: np.ndarray
    ) -> np.ndarray:
        """
        Compute distances between centroids
        
        Args:
            object_centroids: Centroids of tracked objects
            input_centroids: Centroids of detections
        
        Returns:
            Distance matrix
        """
        if len(object_centroids) == 0 or len(input_centroids) == 0:
            return np.zeros((len(object_centroids), len(input_centroids)))
        
        # Compute Euclidean distances
        distances = np.zeros((len(object_centroids), len(input_centroids)))
        
        for i, obj_centroid in enumerate(object_centroids):
            for j, input_centroid in enumerate(input_centroids):
                distances[i, j] = np.linalg.norm(obj_centroid - input_centroid)
        
        return distances
    
    def get_tracked_objects(self) -> Dict[int, TrackedObject]:
        """Get all tracked objects"""
        return self.objects.copy()
    
    def get_active_tracks(self) -> Dict[int, TrackedObject]:
        """Get only active (non-stale) tracks"""
        return {oid: obj for oid, obj in self.objects.items() if not obj.is_stale}
    
    def get_track_count(self) -> int:
        """Get number of active tracks"""
        return len(self.objects)
    
    def reset(self) -> None:
        """Reset tracker"""
        self.objects.clear()
        self.disappeared.clear()
        self.next_object_id = 0
        logger.info("Tracker reset")
