"""Tests for REST API"""

import pytest
from fastapi.testclient import TestClient

from app.api.app import create_app


@pytest.fixture
def client():
    """Create test client"""
    app = create_app()
    return TestClient(app)


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"


class TestAlertsEndpoints:
    """Test alerts endpoints"""
    
    def test_get_alerts(self, client):
        """Test getting alerts"""
        response = client.get("/api/v1/alerts")
        assert response.status_code == 200
        assert "alerts" in response.json()
    
    def test_get_alerts_with_filters(self, client):
        """Test getting alerts with filters"""
        response = client.get("/api/v1/alerts?limit=5&level=warning&hours=12")
        assert response.status_code == 200
        data = response.json()
        assert data["limit"] == 5
        assert data["filters"]["level"] == "warning"
        assert data["filters"]["hours"] == 12
    
    def test_get_specific_alert(self, client):
        """Test getting specific alert"""
        response = client.get("/api/v1/alerts/alert123")
        assert response.status_code == 200
        assert response.json()["alert_id"] == "alert123"
    
    def test_acknowledge_alert(self, client):
        """Test acknowledging alert"""
        response = client.post("/api/v1/alerts/alert123/acknowledge")
        assert response.status_code == 200
        assert response.json()["acknowledged"] is True


class TestStatisticsEndpoints:
    """Test statistics endpoints"""
    
    def test_get_statistics(self, client):
        """Test getting statistics"""
        response = client.get("/api/v1/statistics")
        assert response.status_code == 200
        assert "period_hours" in response.json()
    
    def test_get_statistics_with_hours(self, client):
        """Test getting statistics with custom hours"""
        response = client.get("/api/v1/statistics?hours=48")
        assert response.status_code == 200
        assert response.json()["period_hours"] == 48
    
    def test_get_zone_statistics(self, client):
        """Test getting zone statistics"""
        response = client.get("/api/v1/statistics/zones")
        assert response.status_code == 200
        assert "zones" in response.json()
    
    def test_get_detection_statistics(self, client):
        """Test getting detection statistics"""
        response = client.get("/api/v1/statistics/detections")
        assert response.status_code == 200
        assert "detections" in response.json()


class TestZonesEndpoints:
    """Test zones endpoints"""
    
    def test_get_zones(self, client):
        """Test getting zones"""
        response = client.get("/api/v1/zones")
        assert response.status_code == 200
        assert "zones" in response.json()
    
    def test_get_specific_zone(self, client):
        """Test getting specific zone"""
        response = client.get("/api/v1/zones/zone1")
        assert response.status_code == 200
        assert response.json()["zone_id"] == "zone1"
    
    def test_create_zone(self, client):
        """Test creating zone"""
        zone_data = {
            "id": "zone_new",
            "name": "New Zone",
            "type": "polygon",
            "points": [[0, 0], [100, 0], [100, 100], [0, 100]]
        }
        response = client.post("/api/v1/zones", json=zone_data)
        assert response.status_code == 200
        assert "zone_id" in response.json()
    
    def test_update_zone(self, client):
        """Test updating zone"""
        zone_data = {
            "name": "Updated Zone",
            "type": "rectangle"
        }
        response = client.put("/api/v1/zones/zone1", json=zone_data)
        assert response.status_code == 200
    
    def test_delete_zone(self, client):
        """Test deleting zone"""
        response = client.delete("/api/v1/zones/zone1")
        assert response.status_code == 200


class TestCamerasEndpoints:
    """Test cameras endpoints"""
    
    def test_get_cameras(self, client):
        """Test getting cameras"""
        response = client.get("/api/v1/cameras")
        assert response.status_code == 200
        assert "cameras" in response.json()
    
    def test_get_specific_camera(self, client):
        """Test getting specific camera"""
        response = client.get("/api/v1/cameras/camera1")
        assert response.status_code == 200
        assert response.json()["camera_id"] == "camera1"
    
    def test_add_camera(self, client):
        """Test adding camera"""
        camera_data = {
            "index": 1,
            "width": 1280,
            "height": 720,
            "name": "External Camera"
        }
        response = client.post("/api/v1/cameras", json=camera_data)
        assert response.status_code == 200
        assert "camera_id" in response.json()
    
    def test_remove_camera(self, client):
        """Test removing camera"""
        response = client.delete("/api/v1/cameras/camera1")
        assert response.status_code == 200


class TestSystemEndpoints:
    """Test system endpoints"""
    
    def test_get_system_info(self, client):
        """Test getting system info"""
        response = client.get("/api/v1/system/info")
        assert response.status_code == 200
        assert "version" in response.json()
        assert "status" in response.json()
    
    def test_get_system_config(self, client):
        """Test getting system config"""
        response = client.get("/api/v1/system/config")
        assert response.status_code == 200
        assert "camera" in response.json()
        assert "detection" in response.json()
    
    def test_restart_system(self, client):
        """Test restarting system"""
        response = client.post("/api/v1/system/restart")
        assert response.status_code == 200
        assert "restart" in response.json()["message"].lower()
    
    def test_shutdown_system(self, client):
        """Test shutting down system"""
        response = client.post("/api/v1/system/shutdown")
        assert response.status_code == 200
        assert "shutdown" in response.json()["message"].lower()


class TestRootEndpoint:
    """Test root endpoint"""
    
    def test_root(self, client):
        """Test root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
        assert "version" in response.json()
