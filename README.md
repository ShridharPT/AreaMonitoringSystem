# Area Monitoring System v2.0.0

A production-grade real-time person detection and zone monitoring system using YOLOv8 and advanced computer vision techniques.

## Features

### Core Features
- **Real-time Person Detection**: Uses YOLOv8 for accurate person detection
- **Multi-Zone Monitoring**: Define custom monitoring zones (polygon, rectangle, circle)
- **Smart Alerting**: Configurable alert system with cooldown and rate limiting
- **Persistent Storage**: SQLite database for alerts, detections, and events
- **Auto-Screenshots**: Automatic screenshot capture on person detection
- **GPU Acceleration**: CUDA support for faster inference

### Advanced Features
- **Structured Logging**: Comprehensive logging with file rotation and color output
- **Configuration Management**: Support for environment variables, config files, and defaults
- **Database Management**: Automatic data cleanup and retention policies
- **Statistics Tracking**: Real-time FPS, detection counts, and system metrics
- **Sound Notifications**: Configurable alert sounds

## System Architecture

```
app/
├── core/                 # Core functionality
│   ├── detector.py      # YOLOv8 person detection
│   ├── zones.py         # Zone management
│   └── alerts.py        # Alert management
├── services/            # Background services
│   └── database.py      # SQLite database management
├── utils/               # Utilities
│   ├── logging.py       # Structured logging
│   └── config.py        # Configuration management
└── monitor.py           # Main monitoring application
```

## Installation

### Prerequisites
- Python 3.10 or higher
- CUDA 11.8+ (optional, for GPU acceleration)
- Webcam or video input device

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/area-monitor.git
cd area-monitor
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure the system** (optional)
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

### Basic Usage

```bash
python main.py
```

### Advanced Usage

```bash
# With custom config file
python main.py --config config.json

# Debug mode
python main.py --debug

# Custom log directory
python main.py --log-dir ./custom_logs

# Set log level
python main.py --log-level DEBUG
```

### Keyboard Controls

| Key | Action |
|-----|--------|
| `Q` or `ESC` | Quit application |
| `S` | Take screenshot |

## Configuration

### Configuration File (config.json)

```json
{
  "camera": {
    "index": 0,
    "width": 640,
    "height": 480,
    "fps": 30,
    "name": "Default Camera",
    "enabled": true
  },
  "detection": {
    "confidence_threshold": 0.5,
    "nms_threshold": 0.5,
    "iou_threshold": 0.3,
    "model_path": "yolov8n.pt",
    "use_gpu": true
  },
  "alert": {
    "enabled": true,
    "sound_enabled": true,
    "sound_file": "alert.wav",
    "alert_cooldown": 5.0,
    "max_alerts_per_minute": 10
  },
  "storage": {
    "screenshots_dir": "screenshots",
    "logs_dir": "logs",
    "database_url": "sqlite:///./area_monitor.db",
    "auto_screenshot": true,
    "screenshot_cooldown": 5.0,
    "retention_days": 30
  },
  "ui": {
    "fullscreen": false,
    "show_sidebar": true,
    "show_zones": true,
    "theme": "cyberpunk",
    "fps_limit": 30
  },
  "debug": false,
  "version": "2.0.0"
}
```

### Environment Variables

```bash
# Camera settings
CAMERA_INDEX=0
CAMERA_WIDTH=640
CAMERA_HEIGHT=480
CAMERA_FPS=30

# Detection settings
CONFIDENCE_THRESHOLD=0.5
NMS_THRESHOLD=0.5
MODEL_PATH=yolov8n.pt
USE_GPU=true

# Alert settings
ALERT_ENABLED=true
ALERT_SOUND_ENABLED=true
ALERT_COOLDOWN=5.0

# Storage settings
SCREENSHOTS_DIR=screenshots
LOGS_DIR=logs
AUTO_SCREENSHOT=true
RETENTION_DAYS=30

# Debug
DEBUG=false
USE_ENV_CONFIG=false
```

## API Reference

### AreaMonitor

Main monitoring application class.

```python
from app.monitor import AreaMonitor
from app.utils import load_config

config = load_config("config.json")
monitor = AreaMonitor(config)
monitor.run()
```

### PersonDetector

Person detection using YOLOv8.

```python
from app.core import PersonDetector

detector = PersonDetector(
    model_path="yolov8n.pt",
    confidence_threshold=0.5,
    use_gpu=True
)

detections = detector.detect(frame)
for detection in detections:
    print(f"Person at {detection.center} with confidence {detection.confidence}")
```

### ZoneManager

Zone management for monitoring areas.

```python
from app.core import ZoneManager, Zone, ZoneType

zone_manager = ZoneManager()

zone = Zone(
    id="zone1",
    name="Entrance",
    zone_type=ZoneType.POLYGON,
    points=[(0, 0), (100, 0), (100, 100), (0, 100)]
)

zone_manager.add_zone(zone)
zones_with_point = zone_manager.check_point_in_zones((50, 50))
```

### AlertManager

Alert management and notifications.

```python
from app.core import AlertManager, AlertLevel

alert_manager = AlertManager(
    alert_cooldown=5.0,
    max_alerts_per_minute=10,
    sound_file="alert.wav"
)

alert = alert_manager.create_alert(
    message="Person detected",
    level=AlertLevel.WARNING,
    zone_id="zone1"
)
```

### Database

Persistent storage management.

```python
from app.services import Database

db = Database("area_monitor.db")

# Add alert
db.add_alert("alert_1", "Person detected", "warning", "zone1", 1)

# Get alerts
alerts = db.get_alerts(limit=10, level="warning", hours=24)

# Get statistics
stats = db.get_statistics(hours=24)

# Cleanup old data
db.cleanup_old_data(retention_days=30)
```

## Performance

### Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | Intel i5 / AMD Ryzen 5 | Intel i7 / AMD Ryzen 7 |
| RAM | 4GB | 8GB+ |
| GPU | None | NVIDIA RTX 2060+ |
| Storage | 10GB | 50GB+ |

### Performance Metrics

- **FPS**: 20-30 FPS on CPU, 30+ FPS on GPU
- **Latency**: 50-100ms per frame on CPU, 20-50ms on GPU
- **Memory**: ~500MB base + model size (~100MB for YOLOv8n)

## Troubleshooting

### Camera not detected
```bash
# Check available cameras
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try different camera index
python main.py --config config.json  # Edit camera.index in config
```

### Low FPS
- Reduce camera resolution
- Use GPU acceleration
- Use smaller model (yolov8n instead of yolov8m)
- Reduce detection frequency

### High memory usage
- Reduce screenshot retention
- Enable database cleanup
- Monitor with: `python -m memory_profiler main.py`

## Development

### Running Tests

```bash
pytest tests/ -v
pytest tests/ --cov=app
```

### Code Quality

```bash
# Format code
black app/

# Lint code
flake8 app/

# Type checking
mypy app/
```

### Building Documentation

```bash
cd docs
make html
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Roadmap

### v2.1.0 (Next Release)
- [ ] Multi-camera support
- [ ] Object tracking (DeepSORT)
- [ ] Web dashboard
- [ ] REST API

### v2.2.0
- [ ] Face recognition
- [ ] Crowd density analysis
- [ ] Mobile app
- [ ] Cloud integration

### v3.0.0
- [ ] Distributed processing
- [ ] Advanced analytics
- [ ] Machine learning model training
- [ ] Enterprise features

## Changelog

### v2.0.0 (Current)
- Complete rewrite with production-grade architecture
- Structured logging system
- Persistent database storage
- Enhanced configuration management
- Improved error handling
- Comprehensive documentation

### v1.0.0
- Initial release
- Basic person detection
- Simple zone monitoring
- Alert system

## Authors

- **Development Team** - Initial work and maintenance

## Acknowledgments

- YOLOv8 by Ultralytics
- OpenCV community
- PyTorch team
#   A r e a M o n i t o r i n g S y s t e m  
 