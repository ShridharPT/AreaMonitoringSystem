# Render Deployment Guide

## Area Monitoring System on Render

This guide explains how to deploy the Area Monitoring System on Render.

## Prerequisites

1. **Render Account** - Sign up at https://render.com
2. **GitHub Repository** - Push your code to GitHub
3. **Git** - For version control

## Step 1: Prepare Your Repository

### 1.1 Initialize Git (if not already done)
```bash
cd area-monitor
git init
git add .
git commit -m "Initial commit: Area Monitoring System v2.0.0"
```

### 1.2 Push to GitHub
```bash
git remote add origin https://github.com/yourusername/area-monitor.git
git branch -M main
git push -u origin main
```

## Step 2: Create Render Account

1. Go to https://render.com
2. Sign up with GitHub account
3. Authorize Render to access your repositories

## Step 3: Deploy on Render

### Option 1: Using Render Dashboard (Recommended)

1. **Log in to Render Dashboard**
   - Go to https://dashboard.render.com

2. **Create New Web Service**
   - Click "New +" button
   - Select "Web Service"
   - Connect your GitHub repository
   - Select "area-monitor" repository

3. **Configure Service**
   - **Name**: `area-monitor`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python -m uvicorn app.api.app:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - Click "Advanced"
   - Add environment variables:
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

5. **Configure Resources**
   - **Plan**: Free or Starter
   - **Memory**: 512 MB (minimum)
   - **Disk**: 10 GB
   - **Max Instances**: 1

6. **Deploy**
   - Click "Create Web Service"
   - Wait for deployment (2-5 minutes)

### Option 2: Using render.yaml

1. **Render will automatically detect render.yaml**
   - Ensure `render.yaml` is in repository root
   - Push to GitHub

2. **Deploy**
   - Go to Render Dashboard
   - Click "New +"
   - Select "Blueprint"
   - Connect repository
   - Render will use `render.yaml` configuration

## Step 4: Verify Deployment

### Check Service Status
1. Go to Render Dashboard
2. Click on "area-monitor" service
3. Check "Logs" tab for any errors

### Test API Endpoints
```bash
# Replace YOUR_RENDER_URL with your actual URL
curl https://YOUR_RENDER_URL/api/v1/health

# Get alerts
curl https://YOUR_RENDER_URL/api/v1/alerts

# Get statistics
curl https://YOUR_RENDER_URL/api/v1/statistics
```

### Access Dashboard
```
https://YOUR_RENDER_URL/
```

## Step 5: Configure Custom Domain (Optional)

1. Go to Service Settings
2. Click "Custom Domain"
3. Enter your domain (e.g., monitor.yourdomain.com)
4. Add DNS records as instructed

## Troubleshooting

### Build Fails
- Check `build.sh` script
- Verify `requirements.txt` has all dependencies
- Check Python version compatibility

### Service Won't Start
- Check logs in Render Dashboard
- Verify environment variables are set
- Ensure start command is correct

### High Memory Usage
- Reduce model size (use yolov8n instead of yolov8m)
- Enable database cleanup
- Monitor with Render's metrics

### Database Issues
- SQLite works but is limited
- Consider upgrading to PostgreSQL for production
- Use Render's PostgreSQL add-on

## Production Recommendations

### 1. Use PostgreSQL
```bash
# In Render Dashboard
1. Create PostgreSQL database
2. Update DATABASE_URL environment variable
3. Run migrations
```

### 2. Enable Auto-Deploy
```bash
1. Go to Service Settings
2. Enable "Auto-Deploy"
3. Select branch (main)
```

### 3. Set Up Monitoring
```bash
1. Enable "Notifications"
2. Add email for alerts
3. Set up Slack integration
```

### 4. Configure Backups
```bash
1. Enable database backups
2. Set retention period
3. Test restore process
```

### 5. Use Environment Variables
```bash
# Never hardcode sensitive data
# Use Render's environment variables for:
- API keys
- Database credentials
- Secret tokens
```

## Scaling

### Vertical Scaling (Increase Resources)
1. Go to Service Settings
2. Change Plan to Starter or higher
3. Increase memory allocation
4. Restart service

### Horizontal Scaling
1. Create multiple instances
2. Use load balancer
3. Share database across instances

## Cost Optimization

### Free Plan
- 0.5 GB RAM
- Limited to 750 hours/month
- Spins down after 15 min inactivity
- Good for testing

### Starter Plan
- 0.5 GB RAM
- $7/month
- Always on
- Good for small deployments

### Standard Plan
- 1 GB RAM
- $12/month
- Better performance
- Recommended for production

## Monitoring & Logging

### View Logs
1. Go to Service Dashboard
2. Click "Logs" tab
3. Filter by level (error, warning, info)

### Set Up Alerts
1. Go to Service Settings
2. Enable "Notifications"
3. Add email or Slack webhook

### Performance Metrics
1. Go to "Metrics" tab
2. Monitor CPU, Memory, Disk
3. Check response times

## Updating Deployment

### Deploy New Version
```bash
# Make changes locally
git add .
git commit -m "Update: description"
git push origin main

# Render will auto-deploy if enabled
# Or manually trigger in Dashboard
```

### Rollback to Previous Version
1. Go to Service Dashboard
2. Click "Deployments" tab
3. Select previous deployment
4. Click "Redeploy"

## API Documentation

After deployment, access API docs at:
- **Swagger UI**: `https://YOUR_RENDER_URL/api/docs`
- **ReDoc**: `https://YOUR_RENDER_URL/api/redoc`

## Support

For Render-specific issues:
- **Documentation**: https://render.com/docs
- **Support**: https://render.com/support
- **Status**: https://status.render.com

For Area Monitoring System issues:
- **GitHub Issues**: https://github.com/yourusername/area-monitor/issues
- **Documentation**: See README.md

## Next Steps

1. ✅ Deploy on Render
2. ✅ Test API endpoints
3. ✅ Access dashboard
4. ✅ Configure monitoring
5. ✅ Set up backups
6. ✅ Enable auto-deploy
7. ✅ Monitor performance

---

**Deployment Status**: Ready for Render ✅
