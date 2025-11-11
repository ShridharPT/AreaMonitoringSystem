# Deployment Guide

## Production Deployment

### Prerequisites

- Docker and Docker Compose
- Linux server (Ubuntu 20.04+ recommended)
- NVIDIA GPU (optional, for GPU acceleration)
- NVIDIA Docker runtime (if using GPU)

### System Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| CPU | 4 cores | 8+ cores |
| RAM | 4GB | 8GB+ |
| Storage | 20GB | 100GB+ |
| GPU | None | NVIDIA RTX 2060+ |
| Network | 1Mbps | 10Mbps+ |

## Docker Deployment

### 1. Build Docker Image

```bash
# Clone repository
git clone https://github.com/yourusername/area-monitor.git
cd area-monitor

# Build image
docker build -t area-monitor:2.0.0 .

# Tag for registry
docker tag area-monitor:2.0.0 your-registry/area-monitor:2.0.0
```

### 2. Push to Registry

```bash
# Login to registry
docker login your-registry

# Push image
docker push your-registry/area-monitor:2.0.0
```

### 3. Deploy with Docker Compose

```bash
# Copy docker-compose.yml
cp docker-compose.yml docker-compose.prod.yml

# Edit for production
nano docker-compose.prod.yml

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f area-monitor
```

### 4. Production docker-compose.yml

```yaml
version: '3.8'

services:
  area-monitor:
    image: your-registry/area-monitor:2.0.0
    container_name: area-monitor
    restart: always
    environment:
      - CAMERA_INDEX=0
      - CONFIDENCE_THRESHOLD=0.5
      - ALERT_ENABLED=true
      - AUTO_SCREENSHOT=true
      - DEBUG=false
      - LOG_LEVEL=INFO
    volumes:
      - ./logs:/app/logs
      - ./screenshots:/app/screenshots
      - ./area_monitor.db:/app/area_monitor.db
      - /dev/video0:/dev/video0
    devices:
      - /dev/video0:/dev/video0
    ports:
      - "8000:8000"
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/api/v1/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    networks:
      - monitoring

  prometheus:
    image: prom/prometheus:latest
    container_name: prometheus
    restart: always
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
    networks:
      - monitoring

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: always
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
      - GF_USERS_ALLOW_SIGN_UP=false
    volumes:
      - grafana_data:/var/lib/grafana
    ports:
      - "3000:3000"
    depends_on:
      - prometheus
    networks:
      - monitoring

volumes:
  prometheus_data:
  grafana_data:

networks:
  monitoring:
    driver: bridge
```

## Kubernetes Deployment

### 1. Create Namespace

```bash
kubectl create namespace monitoring
```

### 2. Create ConfigMap

```bash
kubectl create configmap area-monitor-config \
  --from-file=config.json \
  -n monitoring
```

### 3. Create Secret

```bash
kubectl create secret generic area-monitor-secrets \
  --from-literal=db-password=your-password \
  -n monitoring
```

### 4. Deploy Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: area-monitor
  namespace: monitoring
spec:
  replicas: 1
  selector:
    matchLabels:
      app: area-monitor
  template:
    metadata:
      labels:
        app: area-monitor
    spec:
      containers:
      - name: area-monitor
        image: your-registry/area-monitor:2.0.0
        imagePullPolicy: Always
        ports:
        - containerPort: 8000
        env:
        - name: CAMERA_INDEX
          value: "0"
        - name: CONFIDENCE_THRESHOLD
          value: "0.5"
        - name: DEBUG
          value: "false"
        resources:
          requests:
            memory: "2Gi"
            cpu: "1000m"
          limits:
            memory: "4Gi"
            cpu: "2000m"
        volumeMounts:
        - name: logs
          mountPath: /app/logs
        - name: screenshots
          mountPath: /app/screenshots
        - name: config
          mountPath: /app/config
        livenessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /api/v1/health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 5
      volumes:
      - name: logs
        persistentVolumeClaim:
          claimName: area-monitor-logs
      - name: screenshots
        persistentVolumeClaim:
          claimName: area-monitor-screenshots
      - name: config
        configMap:
          name: area-monitor-config
```

### 5. Create Service

```yaml
apiVersion: v1
kind: Service
metadata:
  name: area-monitor
  namespace: monitoring
spec:
  type: LoadBalancer
  ports:
  - port: 8000
    targetPort: 8000
  selector:
    app: area-monitor
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
server {
    listen 443 ssl http2;
    server_name monitor.example.com;

    ssl_certificate /etc/letsencrypt/live/monitor.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/monitor.example.com/privkey.pem;

    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /api/v1/health {
        proxy_pass http://localhost:8000/api/v1/health;
    }
}

server {
    listen 80;
    server_name monitor.example.com;
    return 301 https://$server_name$request_uri;
}
```

## Monitoring and Logging

### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'area-monitor'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

### Log Aggregation

```bash
# Using ELK Stack
docker run -d \
  --name elasticsearch \
  -e discovery.type=single-node \
  docker.elastic.co/elasticsearch/elasticsearch:7.14.0

docker run -d \
  --name kibana \
  -p 5601:5601 \
  docker.elastic.co/kibana/kibana:7.14.0
```

## Backup and Recovery

### Database Backup

```bash
# Backup database
sqlite3 area_monitor.db ".backup area_monitor_backup.db"

# Restore database
sqlite3 area_monitor.db ".restore area_monitor_backup.db"

# Automated backup
0 2 * * * /usr/bin/sqlite3 /app/area_monitor.db ".backup /backups/area_monitor_$(date +\%Y\%m\%d).db"
```

### Screenshots Backup

```bash
# Backup screenshots
tar -czf screenshots_backup_$(date +%Y%m%d).tar.gz screenshots/

# Upload to cloud storage
aws s3 sync screenshots/ s3://my-bucket/screenshots/
```

## Performance Tuning

### Database Optimization

```sql
-- Analyze database
ANALYZE;

-- Vacuum database
VACUUM;

-- Create indices
CREATE INDEX idx_alerts_timestamp ON alerts(timestamp);
CREATE INDEX idx_detections_zone ON detections(zone_id);
```

### System Tuning

```bash
# Increase file descriptors
ulimit -n 65536

# Optimize network
sysctl -w net.core.rmem_max=134217728
sysctl -w net.core.wmem_max=134217728
```

## Security Hardening

### Firewall Configuration

```bash
# Allow only necessary ports
sudo ufw allow 22/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 3000/tcp
sudo ufw allow 9090/tcp
sudo ufw enable
```

### API Authentication

```python
# Add JWT authentication
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer

security = HTTPBearer()

@router.get("/protected")
async def protected_route(credentials = Depends(security)):
    # Verify JWT token
    pass
```

### Database Security

```bash
# Set proper permissions
chmod 600 area_monitor.db

# Enable encryption
# Use SQLCipher for encrypted database
```

## Scaling

### Horizontal Scaling

```yaml
# Kubernetes HPA
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: area-monitor-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: area-monitor
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

### Load Balancing

```bash
# Using HAProxy
global
    maxconn 4096

frontend area-monitor
    bind *:80
    default_backend servers

backend servers
    balance roundrobin
    server server1 localhost:8001
    server server2 localhost:8002
    server server3 localhost:8003
```

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs area-monitor

# Check resource limits
docker stats area-monitor

# Rebuild image
docker build --no-cache -t area-monitor:2.0.0 .
```

### High memory usage

```bash
# Check memory leaks
docker exec area-monitor ps aux

# Limit memory
docker update --memory 2g area-monitor
```

### Database corruption

```bash
# Check database integrity
sqlite3 area_monitor.db "PRAGMA integrity_check;"

# Recover database
sqlite3 area_monitor.db ".recover" | sqlite3 area_monitor_recovered.db
```

## Maintenance

### Regular Tasks

- Monitor disk space
- Rotate logs
- Backup database
- Update dependencies
- Review security patches

### Scheduled Maintenance

```bash
# Daily backup
0 2 * * * /scripts/backup.sh

# Weekly cleanup
0 3 * * 0 /scripts/cleanup.sh

# Monthly update
0 4 1 * * /scripts/update.sh
```

## Support

For deployment issues:
- Check logs
- Review configuration
- Verify resource availability
- Contact support team
