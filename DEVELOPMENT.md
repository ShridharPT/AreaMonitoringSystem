# Development Guide

## Project Structure

```
area-monitor/
├── app/
│   ├── __init__.py
│   ├── core/                 # Core functionality
│   │   ├── detector.py      # YOLOv8 person detection
│   │   ├── zones.py         # Zone management
│   │   ├── alerts.py        # Alert management
│   │   ├── camera.py        # Multi-camera support
│   │   ├── tracker.py       # Object tracking
│   │   └── analytics.py     # Analytics engine
│   ├── api/                 # REST API
│   │   ├── routes.py        # API endpoints
│   │   └── app.py           # FastAPI application
│   ├── services/            # Services
│   │   └── database.py      # Database management
│   ├── utils/               # Utilities
│   │   ├── logging.py       # Logging configuration
│   │   └── config.py        # Configuration management
│   └── monitor.py           # Main monitoring application
├── tests/                   # Test suite
│   ├── test_config.py
│   ├── test_zones.py
│   └── test_alerts.py
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose
├── pytest.ini              # Pytest configuration
├── .gitignore              # Git ignore rules
└── README.md               # Documentation
```

## Development Setup

### Prerequisites
- Python 3.10+
- Git
- Virtual environment tool (venv)

### Installation

1. **Clone repository**
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

4. **Install development dependencies**
```bash
pip install pytest pytest-cov black flake8 mypy
```

## Running the Application

### Development Mode

```bash
# With debug logging
python main.py --debug

# With custom config
python main.py --config config.json

# With specific log level
python main.py --log-level DEBUG
```

### REST API Server

```bash
# Start API server
python -m uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8000

# Access API documentation
# Swagger UI: http://localhost:8000/api/docs
# ReDoc: http://localhost:8000/api/redoc
```

## Testing

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_config.py -v
```

### Run with Coverage

```bash
pytest tests/ --cov=app --cov-report=html
```

### Run Specific Test

```bash
pytest tests/test_zones.py::TestZone::test_polygon_zone_creation -v
```

## Code Quality

### Format Code

```bash
black app/ tests/
```

### Lint Code

```bash
flake8 app/ tests/
```

### Type Checking

```bash
mypy app/ --ignore-missing-imports
```

### Run All Quality Checks

```bash
black app/ tests/
flake8 app/ tests/
mypy app/ --ignore-missing-imports
pytest tests/ --cov=app
```

## Architecture

### Core Components

#### PersonDetector
- Uses YOLOv8 for person detection
- Supports GPU acceleration
- Configurable confidence thresholds

```python
from app.core import PersonDetector

detector = PersonDetector(
    model_path="yolov8n.pt",
    confidence_threshold=0.5,
    use_gpu=True
)

detections = detector.detect(frame)
```

#### ZoneManager
- Manages multiple monitoring zones
- Supports polygon, rectangle, and circle zones
- Point-in-zone detection

```python
from app.core import ZoneManager, Zone, ZoneType

manager = ZoneManager()
zone = Zone(
    id="zone1",
    name="Entrance",
    zone_type=ZoneType.POLYGON,
    points=[(0, 0), (100, 0), (100, 100), (0, 100)]
)
manager.add_zone(zone)
```

#### AlertManager
- Creates and manages alerts
- Implements cooldown and rate limiting
- Sound notifications

```python
from app.core import AlertManager, AlertLevel

alert_manager = AlertManager(
    alert_cooldown=5.0,
    max_alerts_per_minute=10
)

alert = alert_manager.create_alert(
    message="Person detected",
    level=AlertLevel.WARNING
)
```

#### CentroidTracker
- Tracks detected persons across frames
- Uses centroid matching
- Maintains track history

```python
from app.core import CentroidTracker

tracker = CentroidTracker(
    max_disappeared=30,
    max_distance=50.0
)

tracked_objects = tracker.update(detections)
```

#### Analytics
- Collects and analyzes statistics
- Tracks detection trends
- Provides zone and track analytics

```python
from app.core import Analytics

analytics = Analytics(window_size=300)

analytics.record_frame(
    frame_number=1,
    detection_count=5,
    track_count=3,
    confidences=[0.9, 0.85, 0.92, 0.88, 0.91],
    processing_time=0.05,
    fps=30.0
)

stats = analytics.get_frame_statistics()
```

#### MultiCameraManager
- Manages multiple camera inputs
- Threaded frame capture
- Frame synchronization

```python
from app.core import MultiCameraManager

camera_manager = MultiCameraManager()

camera_manager.add_camera(
    camera_id="camera1",
    camera_index=0,
    width=640,
    height=480,
    fps=30
)

frame = camera_manager.get_frame("camera1")
```

### Database Schema

#### Alerts Table
```sql
CREATE TABLE alerts (
    id TEXT PRIMARY KEY,
    message TEXT NOT NULL,
    level TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    zone_id TEXT,
    detection_count INTEGER DEFAULT 0,
    acknowledged BOOLEAN DEFAULT 0
)
```

#### Detections Table
```sql
CREATE TABLE detections (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    zone_id TEXT,
    person_count INTEGER,
    confidence_avg REAL,
    frame_data BLOB
)
```

#### Screenshots Table
```sql
CREATE TABLE screenshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    filepath TEXT NOT NULL,
    reason TEXT,
    person_count INTEGER,
    zone_id TEXT
)
```

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

## API Documentation

### Health Check
```
GET /api/v1/health
```

### Get Alerts
```
GET /api/v1/alerts?limit=10&level=warning&hours=24
```

### Get Statistics
```
GET /api/v1/statistics?hours=24
```

### Get Zones
```
GET /api/v1/zones
```

### Create Zone
```
POST /api/v1/zones
```

### Get Cameras
```
GET /api/v1/cameras
```

## Docker

### Build Image

```bash
docker build -t area-monitor:latest .
```

### Run Container

```bash
docker run -it \
  --device /dev/video0:/dev/video0 \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/screenshots:/app/screenshots \
  area-monitor:latest
```

### Docker Compose

```bash
docker-compose up -d
```

## Debugging

### Enable Debug Logging

```bash
python main.py --debug --log-level DEBUG
```

### Check Logs

```bash
tail -f logs/area_monitor_*.log
```

### Profile Performance

```bash
python -m cProfile -s cumtime main.py
```

## Contributing

### Code Style

- Follow PEP 8
- Use type hints
- Add docstrings
- Keep functions small and focused

### Commit Messages

```
<type>: <subject>

<body>

<footer>
```

Types: feat, fix, docs, style, refactor, test, chore

Example:
```
feat: add multi-camera support

- Implement MultiCameraManager class
- Add camera thread for concurrent frame capture
- Support camera synchronization

Closes #123
```

### Pull Request Process

1. Fork repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'feat: add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request
6. Ensure all tests pass
7. Request review

## Performance Optimization

### Tips

1. **Use GPU acceleration**
   - Set `use_gpu: true` in config
   - Ensure CUDA is installed

2. **Reduce model size**
   - Use `yolov8n.pt` for faster inference
   - Consider quantization for edge devices

3. **Optimize frame processing**
   - Reduce frame resolution
   - Skip frames if needed
   - Use threading for I/O operations

4. **Database optimization**
   - Create indices for frequently queried columns
   - Implement data retention policies
   - Use connection pooling

## Troubleshooting

### Camera not detected

```bash
# Check available cameras
python -c "import cv2; cap = cv2.VideoCapture(0); print(cap.isOpened())"
```

### Low FPS

- Reduce resolution
- Use GPU acceleration
- Use smaller model
- Check CPU/GPU usage

### High memory usage

- Reduce screenshot retention
- Enable database cleanup
- Monitor with memory profiler

### API not responding

- Check if server is running
- Verify port is not in use
- Check firewall settings

## Resources

- [YOLOv8 Documentation](https://docs.ultralytics.com/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [PyTorch Documentation](https://pytorch.org/docs/)

## Support

For issues or questions:
- Open GitHub issue
- Check documentation
- Review troubleshooting section
