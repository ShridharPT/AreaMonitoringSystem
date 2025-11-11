"""
Main monitoring application
Integrates all components for real-time person detection and monitoring
"""

import cv2
import time
import numpy as np
import threading
from typing import Optional, List, Dict, Any
from datetime import datetime
from pathlib import Path

from app.utils import get_logger, load_config, AppConfig
from app.core import PersonDetector, ZoneManager, Zone, ZoneType, AlertManager, AlertLevel
from app.services import Database

logger = get_logger(__name__)


class AreaMonitor:
    """Main monitoring application"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize area monitor
        
        Args:
            config: Application configuration
        """
        self.config = config or load_config()
        
        # Initialize components
        logger.info("Initializing Area Monitor...")
        
        # Detector
        self.detector = PersonDetector(
            model_path=self.config.detection.model_path,
            confidence_threshold=self.config.detection.confidence_threshold,
            nms_threshold=self.config.detection.nms_threshold,
            use_gpu=self.config.detection.use_gpu
        )
        
        # Zone manager
        self.zone_manager = ZoneManager()
        
        # Alert manager
        self.alert_manager = AlertManager(
            alert_cooldown=self.config.alert.alert_cooldown,
            max_alerts_per_minute=self.config.alert.max_alerts_per_minute,
            sound_file=self.config.alert.sound_file if self.config.alert.sound_enabled else None,
            enable_sound=self.config.alert.sound_enabled
        )
        
        # Database
        self.db = Database(self.config.storage.database_url.replace("sqlite:///", ""))
        
        # Camera
        self.cap = cv2.VideoCapture(self.config.camera.index)
        if not self.cap.isOpened():
            raise Exception(f"Failed to open camera {self.config.camera.index}")
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.camera.width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.camera.height)
        
        self.frame_width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        self.frame_height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        
        # Initialize default zones after frame dimensions are set
        self._init_default_zones()
        
        # Create storage directories
        Path(self.config.storage.screenshots_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.storage.logs_dir).mkdir(parents=True, exist_ok=True)
        
        # Statistics
        self.stats = {
            "total_frames": 0,
            "total_detections": 0,
            "fps": 0,
            "uptime": 0
        }
        
        self.running = False
        self.start_time = time.time()
        self.last_screenshot_time = 0
        
        logger.info("Area Monitor initialized successfully")
    
    def _init_default_zones(self) -> None:
        """Initialize default monitoring zones"""
        # Create a default zone covering the entire frame
        default_zone = Zone(
            id="default",
            name="Full Frame",
            zone_type=ZoneType.POLYGON,
            points=[
                (0, 0),
                (self.frame_width, 0),
                (self.frame_width, self.frame_height),
                (0, self.frame_height)
            ],
            color=(0, 255, 255)
        )
        self.zone_manager.add_zone(default_zone)
    
    def process_frame(self, frame: np.ndarray) -> Dict[str, Any]:
        """
        Process a single frame
        
        Args:
            frame: Input frame
        
        Returns:
            Processing results
        """
        # Detect persons
        detections = self.detector.detect(frame)
        
        # Check detections against zones
        persons_in_zones = {}
        for detection in detections:
            center = detection.center
            zones = self.zone_manager.check_point_in_zones(center)
            
            for zone_id in zones:
                if zone_id not in persons_in_zones:
                    persons_in_zones[zone_id] = []
                persons_in_zones[zone_id].append(detection)
        
        # Generate alerts
        for zone_id, zone_detections in persons_in_zones.items():
            if zone_detections:
                zone = self.zone_manager.get_zone(zone_id)
                if zone and zone.alert_on_entry:
                    alert = self.alert_manager.create_alert(
                        message=f"Person detected in zone: {zone.name}",
                        level=AlertLevel.WARNING,
                        zone_id=zone_id,
                        detection_count=len(zone_detections)
                    )
                    
                    if alert:
                        # Store in database
                        self.db.add_alert(
                            alert.id,
                            alert.message,
                            alert.level.value,
                            zone_id,
                            len(zone_detections)
                        )
                        
                        # Auto-screenshot if enabled
                        if self.config.storage.auto_screenshot:
                            self._take_screenshot(frame, f"person_in_{zone_id}")
        
        # Store detection in database
        if persons_in_zones:
            avg_confidence = np.mean([d.confidence for d in detections]) if detections else 0
            self.db.add_detection(
                zone_id="default",
                person_count=len(detections),
                confidence_avg=avg_confidence
            )
        
        # Update statistics
        self.stats["total_frames"] += 1
        self.stats["total_detections"] += len(detections)
        self.stats["uptime"] = int(time.time() - self.start_time)
        
        return {
            "detections": detections,
            "persons_in_zones": persons_in_zones,
            "frame_count": self.stats["total_frames"]
        }
    
    def _take_screenshot(self, frame: np.ndarray, reason: str) -> bool:
        """
        Take a screenshot
        
        Args:
            frame: Frame to save
            reason: Reason for screenshot
        
        Returns:
            True if successful
        """
        current_time = time.time()
        
        # Check cooldown
        if current_time - self.last_screenshot_time < self.config.storage.screenshot_cooldown:
            return False
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")[:-3]
            filename = f"screenshot_{reason}_{timestamp}.jpg"
            filepath = str(Path(self.config.storage.screenshots_dir) / filename)
            
            cv2.imwrite(filepath, frame)
            
            # Store in database
            self.db.add_screenshot(
                filepath=filepath,
                reason=reason,
                person_count=0,
                zone_id="default"
            )
            
            self.last_screenshot_time = current_time
            logger.info(f"Screenshot saved: {filepath}")
            return True
        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False
    
    def run(self) -> None:
        """Main monitoring loop"""
        self.running = True
        logger.info("Starting monitoring loop...")
        
        frame_count = 0
        fps_start_time = time.time()
        
        try:
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame")
                    break
                
                # Process frame
                result = self.process_frame(frame)
                
                # Calculate FPS
                frame_count += 1
                elapsed = time.time() - fps_start_time
                if elapsed >= 1.0:
                    self.stats["fps"] = frame_count / elapsed
                    frame_count = 0
                    fps_start_time = time.time()
                
                # Display frame (optional)
                self._display_frame(frame, result)
                
                # Control frame rate
                time.sleep(1.0 / self.config.camera.fps)
        
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user")
        except Exception as e:
            logger.error(f"Error in monitoring loop: {e}")
        finally:
            self.cleanup()
    
    def _display_frame(self, frame: np.ndarray, result: Dict[str, Any]) -> None:
        """
        Display frame with detections and zones (headless mode)
        
        Args:
            frame: Input frame
            result: Processing result
        """
        try:
            # Draw zones
            frame = self.zone_manager.draw_zones(frame)
            
            # Draw detections
            for detection in result["detections"]:
                x1, y1, x2, y2 = int(detection.x1), int(detection.y1), int(detection.x2), int(detection.y2)
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                
                # Draw confidence
                conf_text = f"{detection.class_name}: {detection.confidence:.2f}"
                cv2.putText(frame, conf_text, (x1, y1 - 10),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            
            # Draw statistics
            stats_text = f"FPS: {self.stats['fps']:.1f} | Detections: {len(result['detections'])}"
            cv2.putText(frame, stats_text, (10, 30),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)
            
            # Try to display (may fail in headless environment)
            try:
                cv2.imshow("Area Monitor", frame)
                
                # Handle key presses
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:  # q or ESC
                    self.running = False
                elif key == ord('s'):  # s for screenshot
                    self._take_screenshot(frame, "manual")
            except cv2.error:
                # Headless mode - just log statistics
                logger.debug(f"Frame {self.stats['total_frames']}: {len(result['detections'])} detections, FPS: {self.stats['fps']:.1f}")
        except Exception as e:
            logger.error(f"Display error: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources"""
        logger.info("Cleaning up resources...")
        
        if self.cap:
            self.cap.release()
        
        try:
            cv2.destroyAllWindows()
        except cv2.error:
            # Headless mode - no windows to destroy
            pass
        
        # Cleanup old data
        self.db.cleanup_old_data(self.config.storage.retention_days)
        
        # Log final statistics
        stats = self.db.get_statistics(hours=24)
        logger.info(f"Final statistics: {stats}")
        
        logger.info("Cleanup complete")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get current statistics"""
        return {
            **self.stats,
            "database_stats": self.db.get_statistics(hours=24),
            "alert_stats": self.alert_manager.get_statistics()
        }
