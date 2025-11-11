"""Tests for configuration management"""

import pytest
import os
import json
import tempfile
from pathlib import Path

from app.utils.config import (
    AppConfig, CameraConfig, DetectionConfig,
    AlertConfig, StorageConfig, UIConfig, load_config
)


class TestCameraConfig:
    """Test camera configuration"""
    
    def test_default_camera_config(self):
        """Test default camera configuration"""
        config = CameraConfig()
        assert config.index == 0
        assert config.width == 640
        assert config.height == 480
        assert config.fps == 30
        assert config.enabled is True
    
    def test_custom_camera_config(self):
        """Test custom camera configuration"""
        config = CameraConfig(
            index=1,
            width=1280,
            height=720,
            fps=60
        )
        assert config.index == 1
        assert config.width == 1280
        assert config.height == 720
        assert config.fps == 60


class TestDetectionConfig:
    """Test detection configuration"""
    
    def test_default_detection_config(self):
        """Test default detection configuration"""
        config = DetectionConfig()
        assert config.confidence_threshold == 0.5
        assert config.nms_threshold == 0.5
        assert config.use_gpu is True
    
    def test_custom_detection_config(self):
        """Test custom detection configuration"""
        config = DetectionConfig(
            confidence_threshold=0.7,
            nms_threshold=0.4
        )
        assert config.confidence_threshold == 0.7
        assert config.nms_threshold == 0.4


class TestAppConfig:
    """Test application configuration"""
    
    def test_default_app_config(self):
        """Test default app configuration"""
        config = AppConfig.get_default()
        assert config.camera is not None
        assert config.detection is not None
        assert config.alert is not None
        assert config.storage is not None
        assert config.ui is not None
    
    def test_config_to_dict(self):
        """Test converting config to dictionary"""
        config = AppConfig.get_default()
        config_dict = config.to_dict()
        
        assert isinstance(config_dict, dict)
        assert "camera" in config_dict
        assert "detection" in config_dict
        assert "alert" in config_dict
    
    def test_config_save_and_load(self):
        """Test saving and loading configuration"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            
            # Create and save config
            original_config = AppConfig.get_default()
            original_config.save(config_path)
            
            # Load config
            loaded_config = AppConfig.load(config_path)
            
            # Verify
            assert loaded_config.camera.width == original_config.camera.width
            assert loaded_config.detection.confidence_threshold == original_config.detection.confidence_threshold
    
    def test_config_from_env(self):
        """Test loading configuration from environment variables"""
        os.environ['CAMERA_INDEX'] = '1'
        os.environ['CONFIDENCE_THRESHOLD'] = '0.7'
        
        config = AppConfig.from_env()
        
        assert config.camera.index == 1
        assert config.detection.confidence_threshold == 0.7
        
        # Cleanup
        del os.environ['CAMERA_INDEX']
        del os.environ['CONFIDENCE_THRESHOLD']


class TestLoadConfig:
    """Test load_config function"""
    
    def test_load_config_default(self):
        """Test loading default configuration"""
        config = load_config()
        assert config is not None
        assert isinstance(config, AppConfig)
    
    def test_load_config_from_file(self):
        """Test loading configuration from file"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            
            # Create config file
            original_config = AppConfig.get_default()
            original_config.save(config_path)
            
            # Load config
            loaded_config = load_config(config_path)
            
            assert loaded_config is not None
            assert loaded_config.camera.width == original_config.camera.width
