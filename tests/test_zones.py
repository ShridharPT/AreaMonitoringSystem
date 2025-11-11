"""Tests for zone management"""

import pytest
import numpy as np

from app.core.zones import Zone, ZoneType, ZoneManager


class TestZone:
    """Test Zone class"""
    
    def test_polygon_zone_creation(self):
        """Test creating a polygon zone"""
        zone = Zone(
            id="zone1",
            name="Test Zone",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        assert zone.id == "zone1"
        assert zone.name == "Test Zone"
        assert zone.zone_type == ZoneType.POLYGON
        assert len(zone.points) == 4
    
    def test_rectangle_zone_creation(self):
        """Test creating a rectangle zone"""
        zone = Zone(
            id="zone2",
            name="Rectangle Zone",
            zone_type=ZoneType.RECTANGLE,
            points=[(0, 0), (100, 100)]
        )
        
        assert zone.zone_type == ZoneType.RECTANGLE
        assert len(zone.points) == 2
    
    def test_circle_zone_creation(self):
        """Test creating a circle zone"""
        zone = Zone(
            id="zone3",
            name="Circle Zone",
            zone_type=ZoneType.CIRCLE,
            points=[(50, 50), (100, 50)]
        )
        
        assert zone.zone_type == ZoneType.CIRCLE
    
    def test_polygon_point_in_zone(self):
        """Test point in polygon detection"""
        zone = Zone(
            id="zone1",
            name="Test Zone",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        # Point inside
        assert zone.contains_point((50, 50)) is True
        
        # Point outside
        assert zone.contains_point((150, 150)) is False
    
    def test_rectangle_point_in_zone(self):
        """Test point in rectangle detection"""
        zone = Zone(
            id="zone2",
            name="Rectangle Zone",
            zone_type=ZoneType.RECTANGLE,
            points=[(0, 0), (100, 100)]
        )
        
        # Point inside
        assert zone.contains_point((50, 50)) is True
        
        # Point outside
        assert zone.contains_point((150, 150)) is False
    
    def test_circle_point_in_zone(self):
        """Test point in circle detection"""
        zone = Zone(
            id="zone3",
            name="Circle Zone",
            zone_type=ZoneType.CIRCLE,
            points=[(50, 50), (100, 50)]  # Center at (50, 50), radius 50
        )
        
        # Point inside
        assert zone.contains_point((50, 50)) is True
        
        # Point outside
        assert zone.contains_point((150, 150)) is False


class TestZoneManager:
    """Test ZoneManager class"""
    
    def test_add_zone(self):
        """Test adding a zone"""
        manager = ZoneManager()
        
        zone = Zone(
            id="zone1",
            name="Test Zone",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        manager.add_zone(zone)
        assert len(manager.get_all_zones()) == 1
    
    def test_remove_zone(self):
        """Test removing a zone"""
        manager = ZoneManager()
        
        zone = Zone(
            id="zone1",
            name="Test Zone",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        manager.add_zone(zone)
        assert len(manager.get_all_zones()) == 1
        
        manager.remove_zone("zone1")
        assert len(manager.get_all_zones()) == 0
    
    def test_get_zone(self):
        """Test getting a zone by ID"""
        manager = ZoneManager()
        
        zone = Zone(
            id="zone1",
            name="Test Zone",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        manager.add_zone(zone)
        retrieved_zone = manager.get_zone("zone1")
        
        assert retrieved_zone is not None
        assert retrieved_zone.id == "zone1"
    
    def test_check_point_in_zones(self):
        """Test checking which zones contain a point"""
        manager = ZoneManager()
        
        zone1 = Zone(
            id="zone1",
            name="Zone 1",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)]
        )
        
        zone2 = Zone(
            id="zone2",
            name="Zone 2",
            zone_type=ZoneType.POLYGON,
            points=[(50, 50), (150, 50), (150, 150), (50, 150)]
        )
        
        manager.add_zone(zone1)
        manager.add_zone(zone2)
        
        # Point in both zones
        zones = manager.check_point_in_zones((75, 75))
        assert len(zones) == 2
        assert "zone1" in zones
        assert "zone2" in zones
        
        # Point in zone1 only
        zones = manager.check_point_in_zones((25, 25))
        assert len(zones) == 1
        assert "zone1" in zones
    
    def test_get_enabled_zones(self):
        """Test getting enabled zones"""
        manager = ZoneManager()
        
        zone1 = Zone(
            id="zone1",
            name="Zone 1",
            zone_type=ZoneType.POLYGON,
            points=[(0, 0), (100, 0), (100, 100), (0, 100)],
            enabled=True
        )
        
        zone2 = Zone(
            id="zone2",
            name="Zone 2",
            zone_type=ZoneType.POLYGON,
            points=[(100, 100), (200, 100), (200, 200), (100, 200)],
            enabled=False
        )
        
        manager.add_zone(zone1)
        manager.add_zone(zone2)
        
        enabled_zones = manager.get_enabled_zones()
        assert len(enabled_zones) == 1
        assert enabled_zones[0].id == "zone1"
