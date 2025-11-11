# Web Dashboard & Render Deployment Guide

## Overview

Your Area Monitoring System now includes:
- ✅ **Modern Web Dashboard** - Real-time monitoring interface
- ✅ **REST API** - 30+ endpoints for integration
- ✅ **Render Deployment** - One-click cloud deployment

---

## Web Dashboard Features

### Dashboard Section
- 📊 Real-time FPS monitoring
- 👥 Current detection count
- 🚨 Alert statistics
- ⏱️ System uptime
- 📈 Performance charts
- 🟢 System status indicator

### Alerts Section
- 📋 Recent alerts list
- 🔍 Filter by severity (Info, Warning, Critical)
- 🗑️ Clear all alerts
- ⏰ Timestamp for each alert

### Zones Section
- 🎯 Monitoring zones management
- ➕ Add new zones
- ✏️ Edit existing zones
- 🗑️ Delete zones
- 📍 Zone type selection (Polygon, Rectangle, Circle)

### Statistics Section
- 📈 Detection trends (24h, 7d, 30d)
- 📊 Alert distribution charts
- 🗺️ Zone activity heatmap
- 💻 System performance metrics

### Settings Section
- 📷 Camera configuration
- 🎯 Detection settings (confidence, NMS threshold)
- 🚨 Alert settings (cooldown, max alerts)
- 🔧 System actions (restart, shutdown, export)

---

## Local Setup

### 1. Start the Application

```bash
# Terminal 1: Start monitoring system
python main.py --debug

# Terminal 2: Start API server
python -m uvicorn app.api.app:app --reload --host 0.0.0.0 --port 8000
```

### 2. Access Dashboard

Open your browser and navigate to:
```
http://localhost:8000
```

### 3. API Documentation

Access interactive API docs at:
```
http://localhost:8000/api/docs
```

---

## Render Deployment

### Step 1: Prepare Repository

```bash
# Initialize git (if not done)
git init
git add .
git commit -m "Area Monitoring System with Web Dashboard"

# Push to GitHub
git remote add origin https://github.com/yourusername/area-monitor.git
git push -u origin main
```

### Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub
3. Authorize Render to access repositories

### Step 3: Deploy on Render

#### Option A: Using Render Dashboard

1. **Log in to Render**
   - Go to https://dashboard.render.com

2. **Create Web Service**
   - Click "New +" → "Web Service"
   - Select your GitHub repository
   - Choose "area-monitor"

3. **Configure Service**
   - **Name**: `area-monitor`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.api.app:app --host 0.0.0.0 --port $PORT`

4. **Environment Variables**
   ```
   PYTHON_VERSION=3.11
   DEBUG=false
   LOG_LEVEL=INFO
   CAMERA_INDEX=0
   CONFIDENCE_THRESHOLD=0.5
   ALERT_ENABLED=true
   AUTO_SCREENSHOT=true
   DATABASE_URL=sqlite:///./area_monitor.db
   ```

5. **Resource Configuration**
   - **Plan**: Free or Starter
   - **Memory**: 512 MB minimum
   - **Disk**: 10 GB
   - **Max Instances**: 1

6. **Deploy**
   - Click "Create Web Service"
   - Wait 2-5 minutes for deployment

#### Option B: Using render.yaml

1. **Render will auto-detect render.yaml**
   - File is already in repository root
   - Push to GitHub

2. **Deploy**
   - Go to Render Dashboard
   - Click "New +" → "Blueprint"
   - Select your repository
   - Render uses render.yaml configuration

### Step 4: Verify Deployment

#### Check Service Status
```bash
# Check if service is running
curl https://YOUR_RENDER_URL/api/v1/health

# Should return:
# {"status": "healthy", "timestamp": "...", "version": "2.0.0"}
```

#### Access Dashboard
```
https://YOUR_RENDER_URL
```

#### Access API Docs
```
https://YOUR_RENDER_URL/api/docs
```

---

## Dashboard Usage

### Monitoring Real-Time Data

1. **View System Status**
   - Check FPS and detection count
   - Monitor alert count
   - Track system uptime

2. **Review Alerts**
   - Filter by severity
   - Check timestamps
   - Clear old alerts

3. **Manage Zones**
   - Add monitoring zones
   - Configure alert triggers
   - View zone statistics

4. **Analyze Statistics**
   - View detection trends
   - Check alert distribution
   - Monitor system performance

5. **Configure Settings**
   - Adjust detection thresholds
   - Set alert parameters
   - Manage camera settings

### API Integration

Use the REST API for custom integrations:

```bash
# Get system health
curl https://YOUR_RENDER_URL/api/v1/health

# Get recent alerts
curl https://YOUR_RENDER_URL/api/v1/alerts?limit=10

# Get statistics
curl https://YOUR_RENDER_URL/api/v1/statistics?hours=24

# Get zones
curl https://YOUR_RENDER_URL/api/v1/zones

# Get cameras
curl https://YOUR_RENDER_URL/api/v1/cameras
```

---

## Render Features

### Auto-Deploy
- Automatically deploy on push to main branch
- No manual deployment needed
- Continuous integration ready

### Health Checks
- Automatic health monitoring
- Restart on failure
- Uptime tracking

### Logs
- Real-time log streaming
- Error tracking
- Performance monitoring

### Metrics
- CPU usage monitoring
- Memory tracking
- Disk space monitoring
- Request metrics

### Scaling
- Vertical scaling (upgrade plan)
- Horizontal scaling (multiple instances)
- Load balancing

---

## Troubleshooting

### Build Fails
```bash
# Check build logs in Render Dashboard
# Common issues:
# 1. Missing dependencies in requirements.txt
# 2. Python version mismatch
# 3. File permission issues

# Solution: Update requirements.txt and push
```

### Service Won't Start
```bash
# Check start command
# Verify environment variables
# Check logs for errors

# Common issues:
# 1. Port not set correctly
# 2. Database connection error
# 3. Missing environment variables
```

### Dashboard Not Loading
```bash
# Check if web files are present
# Verify static file mounting
# Check browser console for errors

# Solution: Ensure app/web/ directory exists with:
# - index.html
# - styles.css
# - dashboard.js
```

### High Memory Usage
```bash
# Reduce model size
# Enable database cleanup
# Monitor with Render metrics

# In settings:
CONFIDENCE_THRESHOLD=0.6  # Higher = fewer detections
AUTO_SCREENSHOT=false     # Disable auto-screenshots
```

---

## Performance Optimization

### For Free Plan
- Use smaller model (yolov8n)
- Disable auto-screenshots
- Reduce detection frequency
- Use SQLite (limited)

### For Starter Plan
- Use standard model (yolov8m)
- Enable auto-screenshots
- Use PostgreSQL database
- Enable caching

### For Production
- Use larger model (yolov8l)
- Enable all features
- Use PostgreSQL with backups
- Set up monitoring and alerts

---

## Monitoring & Maintenance

### Daily Tasks
- Check dashboard for errors
- Review recent alerts
- Monitor system performance

### Weekly Tasks
- Review statistics
- Check database size
- Update configuration if needed

### Monthly Tasks
- Backup database
- Review logs
- Update dependencies
- Optimize performance

---

## Security

### Best Practices
1. **Use HTTPS** - Render provides SSL by default
2. **Set Strong Passwords** - For any authentication
3. **Limit API Access** - Use API keys if needed
4. **Monitor Logs** - Check for suspicious activity
5. **Regular Backups** - Backup database regularly

### Environment Variables
- Never commit secrets to GitHub
- Use Render's environment variable management
- Rotate keys regularly
- Use different keys for different environments

---

## Scaling to Production

### Step 1: Upgrade Plan
```
Free → Starter ($7/month)
Starter → Standard ($12/month)
```

### Step 2: Add PostgreSQL
```
1. Create PostgreSQL database in Render
2. Update DATABASE_URL
3. Run migrations
4. Test connection
```

### Step 3: Enable Backups
```
1. Enable database backups
2. Set retention period
3. Test restore process
```

### Step 4: Set Up Monitoring
```
1. Enable Render notifications
2. Add email alerts
3. Set up Slack integration
4. Configure custom metrics
```

---

## Cost Breakdown

| Component | Free | Starter | Standard |
|-----------|------|---------|----------|
| Web Service | $0 | $7 | $12 |
| PostgreSQL | - | $15 | $15 |
| Total | $0 | $22 | $27 |

---

## Support & Resources

### Documentation
- **Render Docs**: https://render.com/docs
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **Area Monitor Docs**: See README.md

### Troubleshooting
- **Render Support**: https://render.com/support
- **GitHub Issues**: Your repository issues
- **Community**: Render community forums

---

## Next Steps

1. ✅ Deploy on Render
2. ✅ Access dashboard at https://YOUR_RENDER_URL
3. ✅ Configure monitoring zones
4. ✅ Set up alerts
5. ✅ Monitor statistics
6. ✅ Scale to production

---

**Your Area Monitoring System is now live on Render!** 🚀

Access it at: `https://YOUR_RENDER_URL`
