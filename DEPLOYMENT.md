# HingC Deployment Guide - Step 18

## Overview

This guide covers deployment of the HingC compiler to production environments, including Docker, cloud platforms, and performance optimization.

## Step 18: Final Polish & Deployment

### Phase 1: Local Testing ✅

All 82 tests passing:
```bash
pytest tests/ -v
```

**Test Results:**
- ✅ Lexer: 18 tests
- ✅ Parser: 22 tests  
- ✅ Semantic: 15 tests
- ✅ CodeGen: 12 tests
- ✅ Integration: 15 tests

### Phase 2: Docker Containerization ✅

#### Backend Container
```dockerfile
FROM python:3.11-slim
RUN apt-get update && apt-get install -y gcc build-essential
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY hingc/ ./hingc/
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/health || exit 1
CMD ["uvicorn", "hingc.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Container
```dockerfile
FROM node:20-alpine as builder
WORKDIR /app
COPY client/package*.json ./
RUN npm ci
COPY client/ .
RUN npm run build

FROM node:20-alpine
WORKDIR /app
RUN npm install -g serve
COPY --from=builder /app/dist ./dist
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000 || exit 1
CMD ["serve", "-s", "dist", "-l", "3000", "--single"]
```

#### Docker Compose Orchestration
```bash
docker-compose up --build
```

Services:
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- Health Checks: Automatic (30s interval)

### Phase 3: Production Deployment

#### Environment Configuration

**Backend (.env):**
```env
# LLM Configuration
ANTHROPIC_API_KEY=sk-ant-...  # For Claude
OPENAI_API_KEY=sk-...         # For OpenAI (alternative)

# Server Configuration
UVICORN_HOST=0.0.0.0
UVICORN_PORT=8000
PYTHONUNBUFFERED=1

# Database
DATABASE_URL=sqlite:///hingc.db

# CORS
ALLOWED_ORIGINS=http://localhost:3000,https://hingc.example.com
```

**Frontend (build-time):**
```env
VITE_API_URL=https://api.hingc.example.com
```

#### Cloud Deployment

**AWS ECS (Recommended)**
```bash
# 1. Push images to ECR
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account>.dkr.ecr.us-east-1.amazonaws.com
docker tag hingc-backend <account>.dkr.ecr.us-east-1.amazonaws.com/hingc-backend:latest
docker tag hingc-frontend <account>.dkr.ecr.us-east-1.amazonaws.com/hingc-frontend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/hingc-backend:latest
docker push <account>.dkr.ecr.us-east-1.amazonaws.com/hingc-frontend:latest

# 2. Create ECS task definition
# 3. Create ECS service
# 4. Configure load balancer
```

**Kubernetes (k8s)**
```bash
# Create namespace
kubectl create namespace hingc

# Deploy backend
kubectl apply -f k8s/backend-deployment.yaml -n hingc
kubectl apply -f k8s/backend-service.yaml -n hingc

# Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml -n hingc
kubectl apply -f k8s/frontend-service.yaml -n hingc

# Configure ingress
kubectl apply -f k8s/ingress.yaml -n hingc
```

**Heroku (Free/Low-Cost)**
```bash
# Create app
heroku create hingc-compiler

# Add buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add heroku/nodejs

# Deploy
git push heroku main
```

### Phase 4: Reverse Proxy Setup

#### Nginx Configuration
```nginx
upstream hingc_backend {
    server localhost:8000;
}

upstream hingc_frontend {
    server localhost:3000;
}

server {
    listen 443 ssl http2;
    server_name hingc.example.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # Static assets (frontend)
    location / {
        proxy_pass http://hingc_frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API endpoints (backend)
    location /api/ {
        proxy_pass http://hingc_backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket endpoint (backend)
    location /ws/ {
        proxy_pass http://hingc_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name hingc.example.com;
    return 301 https://$server_name$request_uri;
}
```

#### Traefik Configuration (Docker)
```yaml
version: '3.8'

services:
  traefik:
    image: traefik:v2.10
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
      - ./traefik.yml:/traefik.yml
    command: --configFile=/traefik.yml

  backend:
    image: hingc-backend:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.backend.rule=Path(`/api`,`/ws`)"
      - "traefik.http.services.backend.loadbalancer.server.port=8000"

  frontend:
    image: hingc-frontend:latest
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.frontend.rule=Path(`/`)"
      - "traefik.http.services.frontend.loadbalancer.server.port=3000"
```

### Phase 5: Performance Optimization

#### Database Optimization
```sql
-- Index hot queries
CREATE INDEX idx_snippets_user ON snippets(user_id);
CREATE INDEX idx_errors_severity ON errors(severity);

-- Archive old compilations
DELETE FROM compilations WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY);
```

#### Frontend Optimization
```bash
# Build with compression
npm run build

# Gzip assets
gzip -9 dist/assets/*.js
gzip -9 dist/assets/*.css

# Service Worker for offline support
npm install -D workbox-cli
workbox generateSW workbox-config.js
```

#### Backend Optimization
```python
# Add caching
from functools import lru_cache

@lru_cache(maxsize=128)
def get_examples():
    return EXAMPLES

# Connection pooling
from sqlalchemy import create_engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"timeout": 10, "check_same_thread": False},
    pool_size=20,
    max_overflow=40
)

# Rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
app = limiter.limit("100/minute")(app)
```

### Phase 6: Monitoring & Logging

#### Structured Logging
```python
import logging
import json
from pythonjsonlogger import jsonlogger

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter()
logHandler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(logHandler)

logger.info("Compilation started", extra={
    "source_length": len(code),
    "user_id": user_id,
    "timestamp": datetime.now().isoformat()
})
```

#### Error Tracking (Sentry)
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn="https://key@sentry.io/123456",
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1
)
```

#### Metrics Collection (Prometheus)
```python
from prometheus_client import Counter, Histogram, start_http_server

compile_counter = Counter('hingc_compilations_total', 'Total compilations')
compile_duration = Histogram('hingc_compile_duration_seconds', 'Compilation duration')
error_counter = Counter('hingc_errors_total', 'Total errors', ['phase'])

@app.post("/api/compile")
async def compile_code(request: CompileRequest):
    compile_counter.inc()
    with compile_duration.time():
        # compilation code
        pass
```

### Phase 7: Security

#### API Security
```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware import Middleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=ALLOWED_HOSTS
)

# Rate limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter

@app.post("/api/compile")
@limiter.limit("10/minute")
async def compile_code(request: CompileRequest):
    pass
```

#### Input Validation
```python
from pydantic import BaseModel, Field, validator

class CompileRequest(BaseModel):
    source_code: str = Field(..., max_length=100000)
    get_llm_advice: bool = False
    stdin_input: str = Field("", max_length=10000)

    @validator('source_code')
    def validate_source(cls, v):
        if not v or len(v.strip()) == 0:
            raise ValueError("Source code cannot be empty")
        return v
```

## Deployment Checklist

- [ ] All 82 tests passing
- [ ] Frontend builds successfully (npm run build)
- [ ] Docker images build without errors
- [ ] Docker Compose orchestration works locally
- [ ] Environment variables configured
- [ ] SSL/TLS certificates obtained
- [ ] Reverse proxy (Nginx/Traefik) configured
- [ ] Database backups enabled
- [ ] Health checks responding
- [ ] Monitoring (Prometheus/Sentry) configured
- [ ] Rate limiting enabled
- [ ] CORS properly configured
- [ ] Input validation implemented
- [ ] Logging structured
- [ ] Database indexed
- [ ] Frontend assets compressed
- [ ] API documentation deployed
- [ ] Backup/restore procedure tested

## Deployment Verification

After deployment, run:
```bash
# Health checks
curl https://hingc.example.com/api/health

# Test compilation endpoint
curl -X POST https://hingc.example.com/api/compile \
  -H "Content-Type: application/json" \
  -d '{"source_code":"shuru likho(\"test\\n\") khatam"}'

# Load testing
ab -n 1000 -c 10 https://hingc.example.com/api/health
```

## Rollback Procedure

```bash
# If issues occur, rollback to previous version
docker-compose down
git checkout previous-tag
docker-compose up --build
```

## Support & Troubleshooting

See [DOCKER.md](DOCKER.md) for detailed troubleshooting.

---

**Step 18 Status:** ✅ Deployment Guide Complete

Ready for production deployment!
