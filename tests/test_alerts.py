"""Tests for alert management"""

import pytest
import time

from app.core.alerts import Alert, AlertLevel, AlertManager


class TestAlert:
    """Test Alert class"""
    
    def test_alert_creation(self):
        """Test creating an alert"""
        alert = Alert(
            id="alert1",
            message="Test alert",
            level=AlertLevel.WARNING
        )
        
        assert alert.id == "alert1"
        assert alert.message == "Test alert"
        assert alert.level == AlertLevel.WARNING
        assert alert.acknowledged is False
    
    def test_alert_to_dict(self):
        """Test converting alert to dictionary"""
        alert = Alert(
            id="alert1",
            message="Test alert",
            level=AlertLevel.CRITICAL,
            zone_id="zone1",
            detection_count=5
        )
        
        alert_dict = alert.to_dict()
        
        assert alert_dict["id"] == "alert1"
        assert alert_dict["message"] == "Test alert"
        assert alert_dict["level"] == "critical"
        assert alert_dict["zone_id"] == "zone1"
        assert alert_dict["detection_count"] == 5


class TestAlertManager:
    """Test AlertManager class"""
    
    def test_alert_manager_creation(self):
        """Test creating alert manager"""
        manager = AlertManager(
            alert_cooldown=5.0,
            max_alerts_per_minute=10
        )
        
        assert manager.alert_cooldown == 5.0
        assert manager.max_alerts_per_minute == 10
    
    def test_create_alert(self):
        """Test creating an alert"""
        manager = AlertManager(alert_cooldown=0.1)
        
        alert = manager.create_alert(
            message="Test alert",
            level=AlertLevel.WARNING
        )
        
        assert alert is not None
        assert alert.message == "Test alert"
        assert len(manager.alerts) == 1
    
    def test_alert_cooldown(self):
        """Test alert cooldown"""
        manager = AlertManager(alert_cooldown=1.0)
        
        # Create first alert
        alert1 = manager.create_alert(message="Alert 1")
        assert alert1 is not None
        
        # Try to create second alert immediately (should fail)
        alert2 = manager.create_alert(message="Alert 2")
        assert alert2 is None
        
        # Wait for cooldown
        time.sleep(1.1)
        
        # Create alert after cooldown
        alert3 = manager.create_alert(message="Alert 3")
        assert alert3 is not None
    
    def test_force_alert(self):
        """Test forcing an alert regardless of cooldown"""
        manager = AlertManager(alert_cooldown=10.0)
        
        # Create first alert
        alert1 = manager.create_alert(message="Alert 1")
        assert alert1 is not None
        
        # Force create second alert immediately
        alert2 = manager.create_alert(message="Alert 2", force=True)
        assert alert2 is not None
    
    def test_acknowledge_alert(self):
        """Test acknowledging an alert"""
        manager = AlertManager(alert_cooldown=0.1)
        
        alert = manager.create_alert(message="Test alert")
        assert alert.acknowledged is False
        
        manager.acknowledge_alert(alert.id)
        
        retrieved_alert = manager.get_alert(alert.id)
        assert retrieved_alert.acknowledged is True
    
    def test_get_recent_alerts(self):
        """Test getting recent alerts"""
        manager = AlertManager(alert_cooldown=0.01)
        
        # Create multiple alerts
        for i in range(5):
            manager.create_alert(message=f"Alert {i}")
            time.sleep(0.02)
        
        recent = manager.get_recent_alerts(limit=3)
        assert len(recent) == 3
    
    def test_get_unacknowledged_alerts(self):
        """Test getting unacknowledged alerts"""
        manager = AlertManager(alert_cooldown=0.01)
        
        # Create alerts
        alert1 = manager.create_alert(message="Alert 1")
        time.sleep(0.02)
        alert2 = manager.create_alert(message="Alert 2")
        
        # Acknowledge one
        manager.acknowledge_alert(alert1.id)
        
        unacknowledged = manager.get_unacknowledged_alerts()
        assert len(unacknowledged) == 1
        assert unacknowledged[0].id == alert2.id
    
    def test_get_alerts_by_level(self):
        """Test getting alerts by level"""
        manager = AlertManager(alert_cooldown=0.01)
        
        # Create alerts with different levels
        manager.create_alert(message="Warning", level=AlertLevel.WARNING)
        time.sleep(0.02)
        manager.create_alert(message="Critical", level=AlertLevel.CRITICAL)
        time.sleep(0.02)
        manager.create_alert(message="Info", level=AlertLevel.INFO)
        
        warnings = manager.get_alerts_by_level(AlertLevel.WARNING)
        assert len(warnings) == 1
        
        criticals = manager.get_alerts_by_level(AlertLevel.CRITICAL)
        assert len(criticals) == 1
    
    def test_clear_alerts(self):
        """Test clearing all alerts"""
        manager = AlertManager(alert_cooldown=0.01)
        
        # Create alerts
        manager.create_alert(message="Alert 1")
        time.sleep(0.02)
        manager.create_alert(message="Alert 2")
        
        assert len(manager.alerts) == 2
        
        manager.clear_alerts()
        assert len(manager.alerts) == 0
    
    def test_get_statistics(self):
        """Test getting alert statistics"""
        manager = AlertManager(alert_cooldown=0.01)
        
        # Create alerts
        manager.create_alert(message="Warning", level=AlertLevel.WARNING)
        time.sleep(0.02)
        manager.create_alert(message="Critical", level=AlertLevel.CRITICAL)
        
        stats = manager.get_statistics()
        
        assert stats["total_alerts"] == 2
        assert stats["critical"] == 1
        assert stats["warning"] == 1
