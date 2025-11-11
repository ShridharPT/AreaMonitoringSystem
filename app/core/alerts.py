"""
Alert management system
Handles alert creation, storage, and notification
"""

import time
import pygame
import os
from typing import List, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from app.utils import get_logger

logger = get_logger(__name__)


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Alert:
    """Represents an alert"""
    id: str
    message: str
    level: AlertLevel
    timestamp: datetime = field(default_factory=datetime.now)
    zone_id: Optional[str] = None
    detection_count: int = 0
    acknowledged: bool = False
    
    def to_dict(self) -> dict:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "message": self.message,
            "level": self.level.value,
            "timestamp": self.timestamp.isoformat(),
            "zone_id": self.zone_id,
            "detection_count": self.detection_count,
            "acknowledged": self.acknowledged
        }


class AlertManager:
    """Manages alerts and notifications"""
    
    def __init__(
        self,
        alert_cooldown: float = 5.0,
        max_alerts_per_minute: int = 10,
        sound_file: Optional[str] = None,
        enable_sound: bool = True
    ):
        """
        Initialize alert manager
        
        Args:
            alert_cooldown: Minimum time between alerts (seconds)
            max_alerts_per_minute: Maximum alerts allowed per minute
            sound_file: Path to alert sound file
            enable_sound: Enable sound notifications
        """
        self.alert_cooldown = alert_cooldown
        self.max_alerts_per_minute = max_alerts_per_minute
        self.sound_file = sound_file
        self.enable_sound = enable_sound
        
        self.alerts: List[Alert] = []
        self.last_alert_time = 0
        self.alert_times: List[float] = []
        
        # Initialize sound
        self.sound = None
        if self.enable_sound and self.sound_file:
            self._init_sound()
        
        logger.info("Alert manager initialized")
    
    def _init_sound(self) -> None:
        """Initialize alert sound"""
        try:
            if not os.path.exists(self.sound_file):
                logger.warning(f"Alert sound file not found: {self.sound_file}")
                self.sound = None
                return
            
            pygame.mixer.init()
            self.sound = pygame.mixer.Sound(self.sound_file)
            logger.info(f"Alert sound loaded: {self.sound_file}")
        except Exception as e:
            logger.error(f"Failed to load alert sound: {e}")
            self.sound = None
    
    def _can_alert(self) -> bool:
        """Check if alert can be triggered based on cooldown and rate limits"""
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_alert_time < self.alert_cooldown:
            return False
        
        # Check rate limit
        self.alert_times = [t for t in self.alert_times if current_time - t < 60]
        if len(self.alert_times) >= self.max_alerts_per_minute:
            return False
        
        return True
    
    def create_alert(
        self,
        message: str,
        level: AlertLevel = AlertLevel.WARNING,
        zone_id: Optional[str] = None,
        detection_count: int = 0,
        force: bool = False
    ) -> Optional[Alert]:
        """
        Create and trigger an alert
        
        Args:
            message: Alert message
            level: Alert level
            zone_id: Associated zone ID
            detection_count: Number of detections
            force: Force alert regardless of cooldown
        
        Returns:
            Alert object if created, None otherwise
        """
        if not force and not self._can_alert():
            return None
        
        alert_id = f"alert_{int(time.time() * 1000)}"
        alert = Alert(
            id=alert_id,
            message=message,
            level=level,
            zone_id=zone_id,
            detection_count=detection_count
        )
        
        self.alerts.append(alert)
        self.last_alert_time = time.time()
        self.alert_times.append(self.last_alert_time)
        
        # Play sound if enabled
        if self.sound:
            self._play_sound()
        
        logger.info(f"Alert created: {message} (Level: {level.value})")
        
        return alert
    
    def _play_sound(self) -> None:
        """Play alert sound"""
        try:
            if self.sound:
                self.sound.play()
        except Exception as e:
            logger.error(f"Failed to play alert sound: {e}")
    
    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert
        
        Args:
            alert_id: ID of alert to acknowledge
        
        Returns:
            True if alert was acknowledged
        """
        for alert in self.alerts:
            if alert.id == alert_id:
                alert.acknowledged = True
                logger.info(f"Alert acknowledged: {alert_id}")
                return True
        return False
    
    def get_alert(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def get_recent_alerts(self, limit: int = 10) -> List[Alert]:
        """Get recent alerts"""
        return self.alerts[-limit:]
    
    def get_unacknowledged_alerts(self) -> List[Alert]:
        """Get unacknowledged alerts"""
        return [a for a in self.alerts if not a.acknowledged]
    
    def get_alerts_by_level(self, level: AlertLevel) -> List[Alert]:
        """Get alerts by level"""
        return [a for a in self.alerts if a.level == level]
    
    def clear_alerts(self) -> None:
        """Clear all alerts"""
        self.alerts.clear()
        logger.info("All alerts cleared")
    
    def clear_old_alerts(self, max_age_seconds: int = 3600) -> int:
        """
        Clear alerts older than specified time
        
        Args:
            max_age_seconds: Maximum age of alerts to keep
        
        Returns:
            Number of alerts removed
        """
        current_time = datetime.now()
        initial_count = len(self.alerts)
        
        self.alerts = [
            a for a in self.alerts
            if (current_time - a.timestamp).total_seconds() < max_age_seconds
        ]
        
        removed = initial_count - len(self.alerts)
        if removed > 0:
            logger.info(f"Cleared {removed} old alerts")
        
        return removed
    
    def export_alerts(self, filepath: str) -> None:
        """
        Export alerts to JSON file
        
        Args:
            filepath: Path to export file
        """
        import json
        
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w') as f:
            json.dump(
                [a.to_dict() for a in self.alerts],
                f,
                indent=2
            )
        
        logger.info(f"Alerts exported to {filepath}")
    
    def get_statistics(self) -> dict:
        """Get alert statistics"""
        return {
            "total_alerts": len(self.alerts),
            "unacknowledged": len(self.get_unacknowledged_alerts()),
            "critical": len(self.get_alerts_by_level(AlertLevel.CRITICAL)),
            "warning": len(self.get_alerts_by_level(AlertLevel.WARNING)),
            "info": len(self.get_alerts_by_level(AlertLevel.INFO))
        }
