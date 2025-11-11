"""
Configuration management for Area Monitoring System
Supports environment variables, config files, and defaults
"""

import os
import json
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum


class AlertLevel(Enum):
    """Alert severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class CameraConfig:
    """Camera configuration"""
    index: int = 0
    width: int = 640
    height: int = 480
    fps: int = 30
    name: str = "Default Camera"
    enabled: bool = True


@dataclass
class DetectionConfig:
    """Detection configuration"""
    confidence_threshold: float = 0.5
    nms_threshold: float = 0.5
    iou_threshold: float = 0.3
    model_path: str = "yolov8n.pt"
    use_gpu: bool = True


@dataclass
class AlertConfig:
    """Alert configuration"""
    enabled: bool = True
    sound_enabled: bool = True
    sound_file: str = "alert.wav"
    alert_cooldown: float = 5.0
    max_alerts_per_minute: int = 10


@dataclass
class StorageConfig:
    """Storage configuration"""
    screenshots_dir: str = "screenshots"
    logs_dir: str = "logs"
    database_url: str = "sqlite:///./area_monitor.db"
    auto_screenshot: bool = True
    screenshot_cooldown: float = 5.0
    retention_days: int = 30


@dataclass
class UIConfig:
    """UI configuration"""
    fullscreen: bool = False
    show_sidebar: bool = True
    show_zones: bool = True
    theme: str = "cyberpunk"
    fps_limit: int = 30


@dataclass
class AppConfig:
    """Main application configuration"""
    camera: CameraConfig
    detection: DetectionConfig
    alert: AlertConfig
    storage: StorageConfig
    ui: UIConfig
    debug: bool = False
    version: str = "2.0.0"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return asdict(self)
    
    def save(self, path: str) -> None:
        """Save configuration to JSON file"""
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self.to_dict(), f, indent=2)
    
    @classmethod
    def load(cls, path: str) -> 'AppConfig':
        """Load configuration from JSON file"""
        if not os.path.exists(path):
            return cls.get_default()
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        return cls(
            camera=CameraConfig(**data.get('camera', {})),
            detection=DetectionConfig(**data.get('detection', {})),
            alert=AlertConfig(**data.get('alert', {})),
            storage=StorageConfig(**data.get('storage', {})),
            ui=UIConfig(**data.get('ui', {})),
            debug=data.get('debug', False),
            version=data.get('version', "2.0.0")
        )
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables"""
        return cls(
            camera=CameraConfig(
                index=int(os.getenv('CAMERA_INDEX', 0)),
                width=int(os.getenv('CAMERA_WIDTH', 640)),
                height=int(os.getenv('CAMERA_HEIGHT', 480)),
                fps=int(os.getenv('CAMERA_FPS', 30)),
                name=os.getenv('CAMERA_NAME', 'Default Camera'),
                enabled=os.getenv('CAMERA_ENABLED', 'true').lower() == 'true'
            ),
            detection=DetectionConfig(
                confidence_threshold=float(os.getenv('CONFIDENCE_THRESHOLD', 0.5)),
                nms_threshold=float(os.getenv('NMS_THRESHOLD', 0.5)),
                iou_threshold=float(os.getenv('IOU_THRESHOLD', 0.3)),
                model_path=os.getenv('MODEL_PATH', 'yolov8n.pt'),
                use_gpu=os.getenv('USE_GPU', 'true').lower() == 'true'
            ),
            alert=AlertConfig(
                enabled=os.getenv('ALERT_ENABLED', 'true').lower() == 'true',
                sound_enabled=os.getenv('ALERT_SOUND_ENABLED', 'true').lower() == 'true',
                sound_file=os.getenv('ALERT_SOUND_FILE', 'alert.wav'),
                alert_cooldown=float(os.getenv('ALERT_COOLDOWN', 5.0)),
                max_alerts_per_minute=int(os.getenv('MAX_ALERTS_PER_MINUTE', 10))
            ),
            storage=StorageConfig(
                screenshots_dir=os.getenv('SCREENSHOTS_DIR', 'screenshots'),
                logs_dir=os.getenv('LOGS_DIR', 'logs'),
                database_url=os.getenv('DATABASE_URL', 'sqlite:///./area_monitor.db'),
                auto_screenshot=os.getenv('AUTO_SCREENSHOT', 'true').lower() == 'true',
                screenshot_cooldown=float(os.getenv('SCREENSHOT_COOLDOWN', 5.0)),
                retention_days=int(os.getenv('RETENTION_DAYS', 30))
            ),
            ui=UIConfig(
                fullscreen=os.getenv('FULLSCREEN', 'false').lower() == 'true',
                show_sidebar=os.getenv('SHOW_SIDEBAR', 'true').lower() == 'true',
                show_zones=os.getenv('SHOW_ZONES', 'true').lower() == 'true',
                theme=os.getenv('THEME', 'cyberpunk'),
                fps_limit=int(os.getenv('FPS_LIMIT', 30))
            ),
            debug=os.getenv('DEBUG', 'false').lower() == 'true',
            version=os.getenv('APP_VERSION', '2.0.0')
        )
    
    @classmethod
    def get_default(cls) -> 'AppConfig':
        """Get default configuration"""
        return cls(
            camera=CameraConfig(),
            detection=DetectionConfig(),
            alert=AlertConfig(),
            storage=StorageConfig(),
            ui=UIConfig()
        )


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """
    Load configuration from multiple sources in order of priority:
    1. Environment variables
    2. Config file (if provided)
    3. Default configuration
    
    Args:
        config_path: Path to configuration JSON file
    
    Returns:
        AppConfig instance
    """
    # Try to load from environment first
    if os.getenv('USE_ENV_CONFIG', 'false').lower() == 'true':
        return AppConfig.from_env()
    
    # Try to load from config file
    if config_path and os.path.exists(config_path):
        return AppConfig.load(config_path)
    
    # Return default
    return AppConfig.get_default()
