# Quick Start Guide

## 5-Minute Setup

### Option 1: Docker (Recommended)

```bash
# 1. Start the system
docker-compose up -d

# 2. Check status
docker-compose ps

# 3. View logs
docker-compose logs -f area-monitor

# 4. Access services
# - Application: http://localhost:8000
# - Grafana: http://localhost:3000 (admin/admin)
# - Prometheus: http://localhost:9090
```

### Option 2: Local Installation

```bash
# 1. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run application
python main.py

# 4. In another terminal, start API server
python -m uvicorn app.api.app:app --reload
```

## First Run

### 1. Configure Camera
Edit `.env` or `config.json`:
```json
{
  "camera": {
    "index": 0,
    "width": 640,
    "height": 480
  }
}
```

### 2. Set Detection Threshold
```json
{
  "detection": {
    "confidence_threshold": 0.5
  }
}
```

### 3. Enable Alerts
```json
{
  "alert": {
    "enabled": true,
    "sound_enabled": true
  }
}
```

### 4. Start Monitoring
```bash
python main.py --debug
```

## API Quick Reference

### Health Check
```bash
curl http://localhost:8000/api/v1/health
```

### Get Recent Alerts
```bash
curl http://localhost:8000/api/v1/alerts?limit=10
```

### Get Statistics
```bash
curl http://localhost:8000/api/v1/statistics?hours=24
```

### Get Zones
```bash
curl http://localhost:8000/api/v1/zones
```

### Create Zone
```bash
curl -X POST http://localhost:8000/api/v1/zones \
  -H "Content-Type: application/json" \
  -d '{
    "id": "zone1",
    "name": "Entrance",
    "type": "polygon",
    "points": [[0, 0], [100, 0], [100, 100], [0, 100]]
  }'
```

## Common Tasks

### View Logs
```bash
# Real-time logs
tail -f logs/area_monitor_*.log

# Error logs only
tail -f logs/error_*.log

# With grep
grep "ERROR" logs/area_monitor_*.log
```

### Check Database
```bash
# View alerts
sqlite3 area_monitor.db "SELECT * FROM alerts LIMIT 10;"

# View detections
sqlite3 area_monitor.db "SELECT * FROM detections LIMIT 10;"

# Get statistics
sqlite3 area_monitor.db "SELECT COUNT(*) FROM alerts;"
```

### Take Screenshot
Press `S` while application is running, or:
```bash
curl -X POST http://localhost:8000/api/v1/screenshots
```

### Export Data
```bash
# Export alerts
sqlite3 area_monitor.db ".mode json" "SELECT * FROM alerts;" > alerts.json

# Backup database
cp area_monitor.db area_monitor_backup.db
```

## Troubleshooting

### Camera Not Working
```bash
# Check camera availability
python -c "import cv2; print(cv2.VideoCapture(0).isOpened())"

# Try different camera index
python main.py --config config.json  # Edit camera.index
```

### Low FPS
```bash
# Reduce resolution in config.json
"camera": {"width": 320, "height": 240}

# Enable GPU
"detection": {"use_gpu": true}
```

### High Memory Usage
```bash
# Check memory
docker stats area-monitor

# Reduce screenshot retention
"storage": {"retention_days": 7}

# Enable cleanup
sqlite3 area_monitor.db "DELETE FROM screenshots WHERE datetime(timestamp) < datetime('now', '-7 days');"
```

### API Not Responding
```bash
# Check if running
curl http://localhost:8000/api/v1/health

# Check port
netstat -an | grep 8000

# Restart
docker-compose restart area-monitor
```

## Performance Tips

1. **Use GPU** - Set `use_gpu: true` for 2-3x speedup
2. **Reduce Resolution** - Lower resolution = higher FPS
3. **Use Smaller Model** - `yolov8n.pt` is faster than `yolov8m.pt`
4. **Enable Caching** - Use Redis for faster responses
5. **Optimize Database** - Regular cleanup and indexing

## Next Steps

1. **Read Full Documentation** - See README.md
2. **Configure Zones** - Set up monitoring zones
3. **Set Up Alerts** - Configure alert rules
4. **Deploy to Production** - See DEPLOYMENT.md
5. **Integrate with Systems** - Use REST API

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| Q / ESC | Quit |
| S | Screenshot |
| Z | Toggle zones |
| F | Toggle sidebar |
| R | Reset alerts |

## File Locations

| Item | Location |
|------|----------|
| Logs | `logs/` |
| Screenshots | `screenshots/` |
| Database | `area_monitor.db` |
| Config | `config.json` or `.env` |
| API Docs | `http://localhost:8000/api/docs` |

## Support

- **Documentation**: README.md
- **Development**: DEVELOPMENT.md
- **Deployment**: DEPLOYMENT.md
- **API Docs**: http://localhost:8000/api/docs
- **Issues**: GitHub Issues

---

**Ready to monitor!** 🚀
