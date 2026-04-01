# Docker Build & Run Instructions

## Prerequisites
- Docker & Docker Compose installed
- .env file with necessary environment variables (optional)

## Build Images

```bash
# Build both backend and frontend
docker-compose build

# Or build individual services
docker-compose build backend
docker-compose build frontend
```

## Run Containers

```bash
# Start all services
docker-compose up

# Run in background
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Services

### Backend API (Port 8000)
- Health check: http://localhost:8000/api/health
- Compile endpoint: POST http://localhost:8000/api/compile
- Examples endpoint: GET http://localhost:8000/api/examples
- WebSocket: ws://localhost:8000/ws/compile

### Frontend (Port 3000)
- Open in browser: http://localhost:3000
- Automatically connects to backend API

## Docker Images

### Backend (`hingc-backend`)
- Base: Python 3.11 slim
- Includes: GCC, build tools for C compilation
- Dependencies: FastAPI, Uvicorn, Anthropic/OpenAI
- Port: 8000

### Frontend (`hingc-frontend`)
- Base: Node 20 Alpine (builder) + Node 20 Alpine (runtime)
- Multi-stage build for optimized image
- Serves via `serve` utility
- Port: 3000

## Environment Variables

Backend:
- `LLAMA_API_URL`: LLM API endpoint (default: http://localhost:11434)
- `PYTHONUNBUFFERED`: Set to 1 for real-time logs

Frontend:
- `VITE_API_URL`: Backend API URL (default: http://localhost:8000)

## Troubleshooting

```bash
# Check container status
docker-compose ps

# View detailed logs
docker-compose logs backend
docker-compose logs frontend

# Rebuild after code changes
docker-compose build --no-cache

# Remove all containers and volumes
docker-compose down -v
```

## Production Notes

For production deployment:
1. Use environment-specific docker-compose files
2. Add proper secret management (.env files)
3. Configure reverse proxy (Nginx/Traefik)
4. Enable HTTPS with SSL certificates
5. Use production-grade database for persistence
6. Configure resource limits in docker-compose
7. Set up container registry (Docker Hub, ECR, etc.)
