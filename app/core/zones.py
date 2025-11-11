"""
Zone management for area monitoring
Handles zone creation, detection, and visualization
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum
from app.utils import get_logger

logger = get_logger(__name__)


class ZoneType(Enum):
    """Zone types"""
    POLYGON = "polygon"
    RECTANGLE = "rectangle"
    CIRCLE = "circle"


@dataclass
class Zone:
    """Represents a monitoring zone"""
    id: str
    name: str
    zone_type: ZoneType
    points: List[Tuple[float, float]]
    enabled: bool = True
    alert_on_entry: bool = True
    alert_on_exit: bool = False
    color: Tuple[int, int, int] = (0, 255, 255)  # BGR format
    
    def contains_point(self, point: Tuple[float, float]) -> bool:
        """
        Check if point is inside zone
        
        Args:
            point: (x, y) coordinates
        
        Returns:
            True if point is inside zone
        """
        if self.zone_type == ZoneType.POLYGON:
            return self._point_in_polygon(point)
        elif self.zone_type == ZoneType.RECTANGLE:
            return self._point_in_rectangle(point)
        elif self.zone_type == ZoneType.CIRCLE:
            return self._point_in_circle(point)
        return False
    
    def _point_in_polygon(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside polygon using ray casting"""
        x, y = point
        n = len(self.points)
        inside = False
        
        p1x, p1y = self.points[0]
        for i in range(1, n + 1):
            p2x, p2y = self.points[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        
        return inside
    
    def _point_in_rectangle(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside rectangle"""
        if len(self.points) < 2:
            return False
        
        x, y = point
        x1, y1 = self.points[0]
        x2, y2 = self.points[1]
        
        min_x, max_x = min(x1, x2), max(x1, x2)
        min_y, max_y = min(y1, y2), max(y1, y2)
        
        return min_x <= x <= max_x and min_y <= y <= max_y
    
    def _point_in_circle(self, point: Tuple[float, float]) -> bool:
        """Check if point is inside circle"""
        if len(self.points) < 2:
            return False
        
        x, y = point
        cx, cy = self.points[0]
        radius = np.sqrt((self.points[1][0] - cx) ** 2 + (self.points[1][1] - cy) ** 2)
        
        distance = np.sqrt((x - cx) ** 2 + (y - cy) ** 2)
        return distance <= radius


class ZoneManager:
    """Manages multiple monitoring zones"""
    
    def __init__(self):
        """Initialize zone manager"""
        self.zones: dict[str, Zone] = {}
        logger.info("Zone manager initialized")
    
    def add_zone(self, zone: Zone) -> None:
        """
        Add a zone
        
        Args:
            zone: Zone object to add
        """
        self.zones[zone.id] = zone
        logger.info(f"Zone added: {zone.name} (ID: {zone.id})")
    
    def remove_zone(self, zone_id: str) -> bool:
        """
        Remove a zone
        
        Args:
            zone_id: ID of zone to remove
        
        Returns:
            True if zone was removed
        """
        if zone_id in self.zones:
            del self.zones[zone_id]
            logger.info(f"Zone removed: {zone_id}")
            return True
        return False
    
    def get_zone(self, zone_id: str) -> Optional[Zone]:
        """Get zone by ID"""
        return self.zones.get(zone_id)
    
    def get_all_zones(self) -> List[Zone]:
        """Get all zones"""
        return list(self.zones.values())
    
    def get_enabled_zones(self) -> List[Zone]:
        """Get all enabled zones"""
        return [z for z in self.zones.values() if z.enabled]
    
    def check_point_in_zones(self, point: Tuple[float, float]) -> List[str]:
        """
        Check which zones contain a point
        
        Args:
            point: (x, y) coordinates
        
        Returns:
            List of zone IDs containing the point
        """
        zones_containing_point = []
        for zone in self.get_enabled_zones():
            if zone.contains_point(point):
                zones_containing_point.append(zone.id)
        return zones_containing_point
    
    def draw_zones(self, frame: np.ndarray, thickness: int = 2, alpha: float = 0.3) -> np.ndarray:
        """
        Draw zones on frame
        
        Args:
            frame: Input frame
            thickness: Line thickness
            alpha: Transparency (0-1)
        
        Returns:
            Frame with drawn zones
        """
        overlay = frame.copy()
        
        for zone in self.get_enabled_zones():
            if zone.zone_type == ZoneType.POLYGON:
                points = np.array(zone.points, dtype=np.int32)
                cv2.polylines(overlay, [points], True, zone.color, thickness)
                cv2.fillPoly(overlay, [points], zone.color)
            
            elif zone.zone_type == ZoneType.RECTANGLE:
                if len(zone.points) >= 2:
                    pt1 = tuple(map(int, zone.points[0]))
                    pt2 = tuple(map(int, zone.points[1]))
                    cv2.rectangle(overlay, pt1, pt2, zone.color, thickness)
            
            elif zone.zone_type == ZoneType.CIRCLE:
                if len(zone.points) >= 2:
                    center = tuple(map(int, zone.points[0]))
                    radius = int(np.sqrt(
                        (zone.points[1][0] - zone.points[0][0]) ** 2 +
                        (zone.points[1][1] - zone.points[0][1]) ** 2
                    ))
                    cv2.circle(overlay, center, radius, zone.color, thickness)
        
        # Blend overlay with original frame
        return cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
    
    def clear_zones(self) -> None:
        """Clear all zones"""
        self.zones.clear()
        logger.info("All zones cleared")
