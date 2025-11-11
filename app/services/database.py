"""
Database management for Area Monitoring System
Handles persistent storage of alerts, detections, and configurations
"""

import sqlite3
import json
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from pathlib import Path
from app.utils import get_logger

logger = get_logger(__name__)


class Database:
    """SQLite database manager"""
    
    def __init__(self, db_path: str = "area_monitor.db"):
        """
        Initialize database
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
        logger.info(f"Database initialized: {db_path}")
    
    def _init_db(self) -> None:
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Alerts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS alerts (
                id TEXT PRIMARY KEY,
                message TEXT NOT NULL,
                level TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                zone_id TEXT,
                detection_count INTEGER DEFAULT 0,
                acknowledged BOOLEAN DEFAULT 0
            )
        """)
        
        # Detections table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                zone_id TEXT,
                person_count INTEGER,
                confidence_avg REAL,
                frame_data BLOB
            )
        """)
        
        # Screenshots table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS screenshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                filepath TEXT NOT NULL,
                reason TEXT,
                person_count INTEGER,
                zone_id TEXT
            )
        """)
        
        # System events table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                event_type TEXT NOT NULL,
                description TEXT,
                severity TEXT
            )
        """)
        
        # Create indices for better query performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_timestamp ON alerts(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_alerts_level ON alerts(level)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_zone ON detections(zone_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_screenshots_timestamp ON screenshots(timestamp)")
        
        conn.commit()
        conn.close()
    
    def add_alert(
        self,
        alert_id: str,
        message: str,
        level: str,
        zone_id: Optional[str] = None,
        detection_count: int = 0
    ) -> bool:
        """
        Add alert to database
        
        Args:
            alert_id: Unique alert ID
            message: Alert message
            level: Alert level (info, warning, critical)
            zone_id: Associated zone ID
            detection_count: Number of detections
        
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO alerts (id, message, level, zone_id, detection_count)
                VALUES (?, ?, ?, ?, ?)
            """, (alert_id, message, level, zone_id, detection_count))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add alert: {e}")
            return False
    
    def get_alerts(
        self,
        limit: int = 100,
        level: Optional[str] = None,
        zone_id: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        Get alerts from database
        
        Args:
            limit: Maximum number of alerts to return
            level: Filter by level
            zone_id: Filter by zone
            hours: Get alerts from last N hours
        
        Returns:
            List of alert dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM alerts WHERE timestamp > datetime('now', '-' || ? || ' hours')"
            params = [hours]
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if zone_id:
                query += " AND zone_id = ?"
                params.append(zone_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            alerts = [dict(row) for row in cursor.fetchall()]
            
            conn.close()
            return alerts
        except Exception as e:
            logger.error(f"Failed to get alerts: {e}")
            return []
    
    def add_detection(
        self,
        zone_id: Optional[str],
        person_count: int,
        confidence_avg: float
    ) -> bool:
        """
        Add detection record
        
        Args:
            zone_id: Zone where detection occurred
            person_count: Number of persons detected
            confidence_avg: Average confidence score
        
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO detections (zone_id, person_count, confidence_avg)
                VALUES (?, ?, ?)
            """, (zone_id, person_count, confidence_avg))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add detection: {e}")
            return False
    
    def add_screenshot(
        self,
        filepath: str,
        reason: str,
        person_count: int,
        zone_id: Optional[str] = None
    ) -> bool:
        """
        Add screenshot record
        
        Args:
            filepath: Path to screenshot file
            reason: Reason for screenshot
            person_count: Number of persons in screenshot
            zone_id: Associated zone
        
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO screenshots (filepath, reason, person_count, zone_id)
                VALUES (?, ?, ?, ?)
            """, (filepath, reason, person_count, zone_id))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add screenshot: {e}")
            return False
    
    def add_system_event(
        self,
        event_type: str,
        description: str,
        severity: str = "info"
    ) -> bool:
        """
        Add system event
        
        Args:
            event_type: Type of event
            description: Event description
            severity: Event severity
        
        Returns:
            True if successful
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO system_events (event_type, description, severity)
                VALUES (?, ?, ?)
            """, (event_type, description, severity))
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"Failed to add system event: {e}")
            return False
    
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """
        Get statistics for the specified period
        
        Args:
            hours: Number of hours to analyze
        
        Returns:
            Statistics dictionary
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alert statistics
            cursor.execute("""
                SELECT level, COUNT(*) as count FROM alerts
                WHERE timestamp > datetime('now', '-' || ? || ' hours')
                GROUP BY level
            """, (hours,))
            alert_stats = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Detection statistics
            cursor.execute("""
                SELECT COUNT(*) as total, AVG(person_count) as avg_persons,
                       MAX(person_count) as max_persons
                FROM detections
                WHERE timestamp > datetime('now', '-' || ? || ' hours')
            """, (hours,))
            detection_row = cursor.fetchone()
            detection_stats = {
                "total_detections": detection_row[0] or 0,
                "avg_persons": detection_row[1] or 0,
                "max_persons": detection_row[2] or 0
            }
            
            # Screenshot statistics
            cursor.execute("""
                SELECT COUNT(*) as total FROM screenshots
                WHERE timestamp > datetime('now', '-' || ? || ' hours')
            """, (hours,))
            screenshot_count = cursor.fetchone()[0] or 0
            
            conn.close()
            
            return {
                "alerts": alert_stats,
                "detections": detection_stats,
                "screenshots": screenshot_count,
                "period_hours": hours
            }
        except Exception as e:
            logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, retention_days: int = 30) -> int:
        """
        Delete data older than retention period
        
        Args:
            retention_days: Number of days to retain
        
        Returns:
            Number of records deleted
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            
            # Delete old alerts
            cursor.execute(
                "DELETE FROM alerts WHERE timestamp < ?",
                (cutoff_date,)
            )
            alerts_deleted = cursor.rowcount
            
            # Delete old detections
            cursor.execute(
                "DELETE FROM detections WHERE timestamp < ?",
                (cutoff_date,)
            )
            detections_deleted = cursor.rowcount
            
            # Delete old screenshots
            cursor.execute(
                "DELETE FROM screenshots WHERE timestamp < ?",
                (cutoff_date,)
            )
            screenshots_deleted = cursor.rowcount
            
            # Delete old system events
            cursor.execute(
                "DELETE FROM system_events WHERE timestamp < ?",
                (cutoff_date,)
            )
            events_deleted = cursor.rowcount
            
            conn.commit()
            conn.close()
            
            total_deleted = alerts_deleted + detections_deleted + screenshots_deleted + events_deleted
            logger.info(f"Cleaned up {total_deleted} old records")
            
            return total_deleted
        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            return 0
