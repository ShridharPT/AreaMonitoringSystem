"""Tests for database management"""

import pytest
import tempfile
import os
from datetime import datetime, timedelta

from app.services.database import Database


class TestDatabase:
    """Test Database class"""
    
    @pytest.fixture
    def db(self):
        """Create temporary database for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = os.path.join(tmpdir, "test.db")
            database = Database(db_path)
            yield database
    
    def test_database_initialization(self, db):
        """Test database initialization"""
        assert os.path.exists(db.db_path)
    
    def test_add_alert(self, db):
        """Test adding alert to database"""
        result = db.add_alert(
            alert_id="alert1",
            message="Test alert",
            level="warning",
            zone_id="zone1",
            detection_count=5
        )
        assert result is True
    
    def test_get_alerts(self, db):
        """Test retrieving alerts"""
        # Add alerts
        db.add_alert("alert1", "Alert 1", "info")
        db.add_alert("alert2", "Alert 2", "warning")
        db.add_alert("alert3", "Alert 3", "critical")
        
        # Get all alerts
        alerts = db.get_alerts(limit=10)
        assert len(alerts) == 3
    
    def test_get_alerts_by_level(self, db):
        """Test filtering alerts by level"""
        db.add_alert("alert1", "Alert 1", "info")
        db.add_alert("alert2", "Alert 2", "warning")
        db.add_alert("alert3", "Alert 3", "critical")
        
        warnings = db.get_alerts(level="warning")
        assert len(warnings) == 1
        assert warnings[0]["level"] == "warning"
    
    def test_get_alerts_by_zone(self, db):
        """Test filtering alerts by zone"""
        db.add_alert("alert1", "Alert 1", "info", zone_id="zone1")
        db.add_alert("alert2", "Alert 2", "warning", zone_id="zone2")
        
        zone1_alerts = db.get_alerts(zone_id="zone1")
        assert len(zone1_alerts) == 1
        assert zone1_alerts[0]["zone_id"] == "zone1"
    
    def test_add_detection(self, db):
        """Test adding detection record"""
        result = db.add_detection(
            zone_id="zone1",
            person_count=5,
            confidence_avg=0.85
        )
        assert result is True
    
    def test_add_screenshot(self, db):
        """Test adding screenshot record"""
        result = db.add_screenshot(
            filepath="/path/to/screenshot.jpg",
            reason="person_detected",
            person_count=3,
            zone_id="zone1"
        )
        assert result is True
    
    def test_add_system_event(self, db):
        """Test adding system event"""
        result = db.add_system_event(
            event_type="startup",
            description="System started",
            severity="info"
        )
        assert result is True
    
    def test_get_statistics(self, db):
        """Test getting statistics"""
        # Add test data
        db.add_alert("alert1", "Alert 1", "warning")
        db.add_alert("alert2", "Alert 2", "critical")
        db.add_detection("zone1", 5, 0.85)
        
        stats = db.get_statistics(hours=24)
        
        assert "alerts" in stats
        assert "detections" in stats
        assert "screenshots" in stats
    
    def test_cleanup_old_data(self, db):
        """Test cleaning up old data"""
        # Add alert
        db.add_alert("alert1", "Alert 1", "info")
        
        # Cleanup with 0 days retention (should delete everything)
        deleted = db.cleanup_old_data(retention_days=0)
        
        # Verify deletion
        alerts = db.get_alerts(limit=10)
        assert len(alerts) == 0
