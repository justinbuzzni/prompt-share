# Docker Deployment Guide

This guide provides detailed instructions for deploying Prompt Share using Docker and Docker Compose.

## 🐳 Docker Architecture

The application consists of three main services:

1. **MongoDB** - Database for storing conversation data
2. **Backend** - Python FastAPI server
3. **Frontend** - React application served by Nginx

## 📋 Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- 4GB+ available RAM
- Claude Desktop App with local conversation data

## 🚀 Quick Start

### 1. Clone and Setup
```bash
git clone https://github.com/justinbuzzni/prompt-share.git
cd prompt-share
cp .env.example .env
```

### 2. Configure Environment
Edit `.env` file:
```env
# MongoDB Configuration
MONGODB_USER=admin
MONGODB_PASSWORD=your_secure_password
MONGODB_DATABASE=prompt_share

# Claude Data Path (important for Docker volume)
CLAUDE_DATA_PATH=/Users/yourusername/.claude
```

### 3. Start Services
```bash
# Production mode
./docker-start.sh

# Development mode
./docker-start.sh --dev

# Force rebuild
./docker-start.sh --rebuild
```

## 🔧 Configuration Options

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `MONGODB_USER` | MongoDB admin username | `admin` | Yes |
| `MONGODB_PASSWORD` | MongoDB admin password | `password` | Yes |
| `MONGODB_DATABASE` | Database name | `prompt_share` | Yes |
| `CLAUDE_DATA_PATH` | Path to Claude data directory | `~/.claude` | Yes |
| `NODE_ENV` | Application environment | `production` | No |

### Volume Mounts

#### Important: Claude Data Directory
The most critical configuration is mapping your local Claude data directory:

**macOS:**
```env
CLAUDE_DATA_PATH=/Users/yourusername/.claude
```

**Linux:**
```env
CLAUDE_DATA_PATH=/home/yourusername/.claude
```

**Windows:**
```env
CLAUDE_DATA_PATH=C:/Users/yourusername/.claude
```

### Service Ports

| Service | Internal Port | External Port | Description |
|---------|---------------|---------------|-------------|
| Frontend | 80 | 3000 | React application |
| Backend | 8000 | 8000 | FastAPI server |
| MongoDB | 27017 | 27017 | Database server |

## 📝 Docker Compose Files

### Production: `docker-compose.yml`
- Optimized builds with multi-stage Dockerfiles
- Health checks for all services
- Production-ready Nginx configuration
- Persistent MongoDB data volume

### Development: `docker-compose.dev.yml`
- Development-friendly configuration
- Source code volume mounting for live reload
- Simplified service dependencies
- Development MongoDB instance

## 🔍 Service Details

### MongoDB Service
```yaml
services:
  mongodb:
    image: mongo:7.0
    environment:
      MONGO_INITDB_ROOT_USERNAME: ${MONGODB_USER}
      MONGO_INITDB_ROOT_PASSWORD: ${MONGODB_PASSWORD}
    volumes:
      - mongodb_data:/data/db
      - ./docker/mongodb/init-mongo.js:/docker-entrypoint-initdb.d/
```

**Features:**
- Automatic database initialization
- Index creation for optimal performance
- Persistent data storage
- Health checks

### Backend Service
```yaml
services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile
    environment:
      - MONGODB_URL=mongodb://admin:password@mongodb:27017/prompt_share
    volumes:
      - ${CLAUDE_DATA_PATH}:/home/appuser/.claude:ro
```

**Features:**
- Non-root user execution
- Health check endpoint
- Read-only Claude data access
- Environment-based configuration

### Frontend Service
```yaml
services:
  frontend:
    build:
      context: ./claude-viewer-frontend
      dockerfile: Dockerfile
    ports:
      - "3000:80"
```

**Features:**
- Multi-stage build (build + nginx)
- Optimized Nginx configuration
- API proxy to backend
- Security headers
- Static asset caching

## 🛠️ Management Commands

### Starting Services
```bash
# Start in background
docker-compose up -d

# Start with logs
docker-compose up

# Start specific service
docker-compose up mongodb
```

### Stopping Services
```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# Stop specific service
docker-compose stop backend
```

### Viewing Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 frontend
```

### Health Checks
```bash
# Check service status
docker-compose ps

# Check health status
docker-compose exec backend curl http://localhost:8000/health

# MongoDB health
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

## 🔧 Troubleshooting

### Common Issues

#### 1. MongoDB Connection Failed
```bash
# Check MongoDB logs
docker-compose logs mongodb

# Verify MongoDB is running
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

#### 2. Backend Cannot Access Claude Data
```bash
# Verify volume mount
docker-compose exec backend ls -la /home/appuser/.claude

# Check permissions
ls -la ~/.claude
```

#### 3. Frontend Build Fails
```bash
# Rebuild frontend
docker-compose build --no-cache frontend

# Check build logs
docker-compose logs frontend
```

#### 4. Port Conflicts
```bash
# Check what's using the port
lsof -i :3000
lsof -i :8000
lsof -i :27017

# Change ports in docker-compose.yml
```

### Debug Mode

Enable debug logging:
```bash
# Set environment variable
export COMPOSE_LOG_LEVEL=DEBUG

# Run with debug
docker-compose --log-level DEBUG up
```

### Container Access
```bash
# Access backend container
docker-compose exec backend bash

# Access MongoDB shell
docker-compose exec mongodb mongosh

# Access frontend container
docker-compose exec frontend sh
```

## 📊 Performance Tuning

### Resource Limits
Add resource limits to prevent container resource exhaustion:

```yaml
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
          cpus: '0.5'
        reservations:
          memory: 512M
          cpus: '0.25'
```

### MongoDB Optimization
```yaml
services:
  mongodb:
    command: mongod --wiredTigerCacheSizeGB 1.5
```

## 🔒 Security Considerations

### 1. Environment Variables
- Never commit `.env` files to version control
- Use strong passwords for MongoDB
- Rotate credentials regularly

### 2. Network Security
```yaml
networks:
  prompt-share-network:
    driver: bridge
    internal: true  # Isolate from external networks
```

### 3. Container Security
- Services run as non-root users
- Read-only file systems where possible
- Minimal base images

### 4. Data Protection
```yaml
volumes:
  mongodb_data:
    driver: local
    driver_opts:
      type: none
      o: bind
      device: /secure/path/mongodb_data
```

## 🚀 Production Deployment

### 1. Environment Preparation
```bash
# Create production environment file
cp .env.example .env.production

# Set production values
MONGODB_PASSWORD=very_secure_password
NODE_ENV=production
```

### 2. SSL/TLS Setup
Add reverse proxy (nginx/traefik) for HTTPS:

```yaml
# docker-compose.prod.yml
services:
  nginx-proxy:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/ssl:/etc/nginx/ssl
      - ./nginx/conf.d:/etc/nginx/conf.d
```

### 3. Monitoring
```yaml
services:
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
  
  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
```

## 📋 Maintenance

### Regular Tasks

#### 1. Update Images
```bash
# Pull latest images
docker-compose pull

# Rebuild and restart
docker-compose up --build -d
```

#### 2. Backup MongoDB
```bash
# Create backup
docker-compose exec mongodb mongodump --out /backup

# Restore backup
docker-compose exec mongodb mongorestore /backup
```

#### 3. Clean Up
```bash
# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune

# Remove unused containers
docker container prune
```

## 🆘 Support

For Docker-related issues:
1. Check the logs: `docker-compose logs`
2. Verify configuration: `docker-compose config`
3. Test connectivity: Use health check endpoints
4. Review resource usage: `docker stats`

For application issues, refer to the main README.md file.