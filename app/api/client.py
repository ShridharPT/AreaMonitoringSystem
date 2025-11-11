"""
REST API Client for Area Monitoring System
Provides Python client for interacting with the API
"""

import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin
from app.utils import get_logger

logger = get_logger(__name__)


class AreaMonitorClient:
    """Python client for Area Monitoring System API"""
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: int = 10,
        verify_ssl: bool = True
    ):
        """
        Initialize API client
        
        Args:
            base_url: Base URL of API server
            timeout: Request timeout in seconds
            verify_ssl: Verify SSL certificates
        """
        self.base_url = base_url
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.session = requests.Session()
        
        logger.info(f"API client initialized: {base_url}")
    
    def _request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Make HTTP request
        
        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request arguments
        
        Returns:
            Response JSON
        """
        url = urljoin(self.base_url, endpoint)
        
        try:
            response = self.session.request(
                method,
                url,
                timeout=self.timeout,
                verify=self.verify_ssl,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {e}")
            raise
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        return self._request("GET", "/api/v1/health")
    
    # Alerts
    def get_alerts(
        self,
        limit: int = 10,
        level: Optional[str] = None,
        zone_id: Optional[str] = None,
        hours: int = 24
    ) -> Dict[str, Any]:
        """Get alerts"""
        params = {
            "limit": limit,
            "hours": hours
        }
        if level:
            params["level"] = level
        if zone_id:
            params["zone_id"] = zone_id
        
        return self._request("GET", "/api/v1/alerts", params=params)
    
    def get_alert(self, alert_id: str) -> Dict[str, Any]:
        """Get specific alert"""
        return self._request("GET", f"/api/v1/alerts/{alert_id}")
    
    def acknowledge_alert(self, alert_id: str) -> Dict[str, Any]:
        """Acknowledge alert"""
        return self._request("POST", f"/api/v1/alerts/{alert_id}/acknowledge")
    
    # Statistics
    def get_statistics(self, hours: int = 24) -> Dict[str, Any]:
        """Get statistics"""
        return self._request("GET", "/api/v1/statistics", params={"hours": hours})
    
    def get_zone_statistics(self, zone_id: Optional[str] = None) -> Dict[str, Any]:
        """Get zone statistics"""
        params = {}
        if zone_id:
            params["zone_id"] = zone_id
        
        return self._request("GET", "/api/v1/statistics/zones", params=params)
    
    def get_detection_statistics(self, minutes: int = 60) -> Dict[str, Any]:
        """Get detection statistics"""
        return self._request(
            "GET",
            "/api/v1/statistics/detections",
            params={"minutes": minutes}
        )
    
    # Zones
    def get_zones(self) -> Dict[str, Any]:
        """Get all zones"""
        return self._request("GET", "/api/v1/zones")
    
    def get_zone(self, zone_id: str) -> Dict[str, Any]:
        """Get specific zone"""
        return self._request("GET", f"/api/v1/zones/{zone_id}")
    
    def create_zone(self, zone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create zone"""
        return self._request("POST", "/api/v1/zones", json=zone_data)
    
    def update_zone(self, zone_id: str, zone_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update zone"""
        return self._request("PUT", f"/api/v1/zones/{zone_id}", json=zone_data)
    
    def delete_zone(self, zone_id: str) -> Dict[str, Any]:
        """Delete zone"""
        return self._request("DELETE", f"/api/v1/zones/{zone_id}")
    
    # Cameras
    def get_cameras(self) -> Dict[str, Any]:
        """Get all cameras"""
        return self._request("GET", "/api/v1/cameras")
    
    def get_camera(self, camera_id: str) -> Dict[str, Any]:
        """Get specific camera"""
        return self._request("GET", f"/api/v1/cameras/{camera_id}")
    
    def add_camera(self, camera_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add camera"""
        return self._request("POST", "/api/v1/cameras", json=camera_data)
    
    def remove_camera(self, camera_id: str) -> Dict[str, Any]:
        """Remove camera"""
        return self._request("DELETE", f"/api/v1/cameras/{camera_id}")
    
    # System
    def get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return self._request("GET", "/api/v1/system/info")
    
    def get_system_config(self) -> Dict[str, Any]:
        """Get system configuration"""
        return self._request("GET", "/api/v1/system/config")
    
    def restart_system(self) -> Dict[str, Any]:
        """Restart system"""
        return self._request("POST", "/api/v1/system/restart")
    
    def shutdown_system(self) -> Dict[str, Any]:
        """Shutdown system"""
        return self._request("POST", "/api/v1/system/shutdown")
    
    def close(self) -> None:
        """Close session"""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == "__main__":
    # Using context manager
    with AreaMonitorClient("http://localhost:8000") as client:
        # Check health
        health = client.health_check()
        print(f"Health: {health}")
        
        # Get alerts
        alerts = client.get_alerts(limit=5)
        print(f"Alerts: {alerts}")
        
        # Get statistics
        stats = client.get_statistics(hours=24)
        print(f"Statistics: {stats}")
        
        # Get zones
        zones = client.get_zones()
        print(f"Zones: {zones}")
