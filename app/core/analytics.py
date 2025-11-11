"""
Analytics module
Provides statistics and analysis of detection and tracking data
"""

import numpy as np
from typing import Dict, List, Optional, Tuple
from collections import defaultdict, deque
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from app.utils import get_logger

logger = get_logger(__name__)


@dataclass
class FrameStatistics:
    """Statistics for a single frame"""
    timestamp: datetime
    frame_number: int
    detection_count: int
    track_count: int
    avg_confidence: float
    processing_time: float
    fps: float


@dataclass
class ZoneStatistics:
    """Statistics for a zone"""
    zone_id: str
    total_detections: int = 0
    total_entries: int = 0
    total_exits: int = 0
    peak_occupancy: int = 0
    current_occupancy: int = 0
    avg_confidence: float = 0.0
    last_detection: Optional[datetime] = None


class Analytics:
    """Analytics engine for monitoring system"""
    
    def __init__(self, window_size: int = 300):
        """
        Initialize analytics
        
        Args:
            window_size: Size of sliding window for statistics (frames)
        """
        self.window_size = window_size
        
        # Frame statistics
        self.frame_stats: deque = deque(maxlen=window_size)
        self.frame_count = 0
        
        # Zone statistics
        self.zone_stats: Dict[str, ZoneStatistics] = defaultdict(
            lambda: ZoneStatistics(zone_id="")
        )
        
        # Detection history
        self.detection_history: deque = deque(maxlen=window_size)
        
        # Track statistics
        self.track_history: Dict[int, List[Tuple[datetime, Tuple[float, float]]]] = {}
        
        logger.info("Analytics engine initialized")
    
    def record_frame(
        self,
        frame_number: int,
        detection_count: int,
        track_count: int,
        confidences: List[float],
        processing_time: float,
        fps: float
    ) -> None:
        """
        Record frame statistics
        
        Args:
            frame_number: Frame number
            detection_count: Number of detections
            track_count: Number of active tracks
            confidences: List of detection confidences
            processing_time: Time to process frame
            fps: Current FPS
        """
        avg_confidence = np.mean(confidences) if confidences else 0.0
        
        stats = FrameStatistics(
            timestamp=datetime.now(),
            frame_number=frame_number,
            detection_count=detection_count,
            track_count=track_count,
            avg_confidence=avg_confidence,
            processing_time=processing_time,
            fps=fps
        )
        
        self.frame_stats.append(stats)
        self.detection_history.append((datetime.now(), detection_count))
        self.frame_count += 1
    
    def record_zone_detection(
        self,
        zone_id: str,
        detection_count: int,
        confidences: List[float]
    ) -> None:
        """
        Record detection in zone
        
        Args:
            zone_id: Zone identifier
            detection_count: Number of detections
            confidences: List of confidences
        """
        if zone_id not in self.zone_stats:
            self.zone_stats[zone_id] = ZoneStatistics(zone_id=zone_id)
        
        stats = self.zone_stats[zone_id]
        stats.total_detections += detection_count
        stats.current_occupancy = detection_count
        stats.peak_occupancy = max(stats.peak_occupancy, detection_count)
        stats.last_detection = datetime.now()
        
        if confidences:
            stats.avg_confidence = np.mean(confidences)
    
    def record_zone_entry(self, zone_id: str) -> None:
        """Record person entry to zone"""
        if zone_id not in self.zone_stats:
            self.zone_stats[zone_id] = ZoneStatistics(zone_id=zone_id)
        
        self.zone_stats[zone_id].total_entries += 1
    
    def record_zone_exit(self, zone_id: str) -> None:
        """Record person exit from zone"""
        if zone_id not in self.zone_stats:
            self.zone_stats[zone_id] = ZoneStatistics(zone_id=zone_id)
        
        self.zone_stats[zone_id].total_exits += 1
    
    def record_track(
        self,
        track_id: int,
        centroid: Tuple[float, float]
    ) -> None:
        """
        Record track position
        
        Args:
            track_id: Track identifier
            centroid: Track centroid (x, y)
        """
        if track_id not in self.track_history:
            self.track_history[track_id] = []
        
        self.track_history[track_id].append((datetime.now(), centroid))
    
    def get_frame_statistics(self) -> Dict:
        """Get current frame statistics"""
        if not self.frame_stats:
            return {}
        
        stats_list = list(self.frame_stats)
        
        detection_counts = [s.detection_count for s in stats_list]
        track_counts = [s.track_count for s in stats_list]
        confidences = [s.avg_confidence for s in stats_list]
        processing_times = [s.processing_time for s in stats_list]
        fps_values = [s.fps for s in stats_list]
        
        return {
            "total_frames": self.frame_count,
            "avg_detections": np.mean(detection_counts) if detection_counts else 0,
            "max_detections": max(detection_counts) if detection_counts else 0,
            "avg_tracks": np.mean(track_counts) if track_counts else 0,
            "max_tracks": max(track_counts) if track_counts else 0,
            "avg_confidence": np.mean(confidences) if confidences else 0,
            "avg_processing_time": np.mean(processing_times) if processing_times else 0,
            "avg_fps": np.mean(fps_values) if fps_values else 0,
            "max_fps": max(fps_values) if fps_values else 0
        }
    
    def get_zone_statistics(self, zone_id: Optional[str] = None) -> Dict:
        """
        Get zone statistics
        
        Args:
            zone_id: Specific zone or None for all zones
        
        Returns:
            Zone statistics
        """
        if zone_id:
            if zone_id in self.zone_stats:
                stats = self.zone_stats[zone_id]
                return {
                    "zone_id": zone_id,
                    "total_detections": stats.total_detections,
                    "total_entries": stats.total_entries,
                    "total_exits": stats.total_exits,
                    "peak_occupancy": stats.peak_occupancy,
                    "current_occupancy": stats.current_occupancy,
                    "avg_confidence": stats.avg_confidence,
                    "last_detection": stats.last_detection.isoformat() if stats.last_detection else None
                }
            return {}
        
        # Return all zones
        result = {}
        for zid, stats in self.zone_stats.items():
            result[zid] = {
                "zone_id": zid,
                "total_detections": stats.total_detections,
                "total_entries": stats.total_entries,
                "total_exits": stats.total_exits,
                "peak_occupancy": stats.peak_occupancy,
                "current_occupancy": stats.current_occupancy,
                "avg_confidence": stats.avg_confidence,
                "last_detection": stats.last_detection.isoformat() if stats.last_detection else None
            }
        
        return result
    
    def get_detection_trend(self, minutes: int = 10) -> List[Tuple[datetime, int]]:
        """
        Get detection trend over time
        
        Args:
            minutes: Time window in minutes
        
        Returns:
            List of (timestamp, count) tuples
        """
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        
        trend = [
            (ts, count) for ts, count in self.detection_history
            if ts >= cutoff_time
        ]
        
        return trend
    
    def get_track_statistics(self, track_id: Optional[int] = None) -> Dict:
        """
        Get track statistics
        
        Args:
            track_id: Specific track or None for all tracks
        
        Returns:
            Track statistics
        """
        if track_id:
            if track_id in self.track_history:
                positions = self.track_history[track_id]
                if positions:
                    centroids = np.array([p[1] for p in positions])
                    distances = np.linalg.norm(
                        np.diff(centroids, axis=0),
                        axis=1
                    )
                    
                    return {
                        "track_id": track_id,
                        "positions": len(positions),
                        "total_distance": float(np.sum(distances)),
                        "avg_speed": float(np.mean(distances)) if len(distances) > 0 else 0,
                        "duration": (positions[-1][0] - positions[0][0]).total_seconds()
                    }
            return {}
        
        # Return all tracks
        result = {}
        for tid, positions in self.track_history.items():
            if positions:
                centroids = np.array([p[1] for p in positions])
                distances = np.linalg.norm(
                    np.diff(centroids, axis=0),
                    axis=1
                )
                
                result[tid] = {
                    "track_id": tid,
                    "positions": len(positions),
                    "total_distance": float(np.sum(distances)),
                    "avg_speed": float(np.mean(distances)) if len(distances) > 0 else 0,
                    "duration": (positions[-1][0] - positions[0][0]).total_seconds()
                }
        
        return result
    
    def get_summary(self) -> Dict:
        """Get comprehensive summary"""
        return {
            "frame_statistics": self.get_frame_statistics(),
            "zone_statistics": self.get_zone_statistics(),
            "track_statistics": self.get_track_statistics(),
            "timestamp": datetime.now().isoformat()
        }
    
    def reset(self) -> None:
        """Reset all statistics"""
        self.frame_stats.clear()
        self.zone_stats.clear()
        self.detection_history.clear()
        self.track_history.clear()
        self.frame_count = 0
        logger.info("Analytics reset")
