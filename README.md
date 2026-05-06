# URL Shortener — Multi-Service Deployment Platform

A production-grade URL shortener built with microservices architecture, deployed on Kubernetes with full CI/CD and monitoring.

## Tech Stack

| Component | Technology |
|-----------|------------|
| Frontend | React 18 + Vite |
| Backend | Python FastAPI |
| Database | PostgreSQL 15 |
| Cache | Redis 7 |
| Containers | Docker (multi-stage builds) |
| Orchestration | Kubernetes + Helm |
| CI/CD | GitHub Actions |
| Monitoring | Prometheus + Grafana |

## Quick Start

```bash
# Clone the repo
git clone <repo-url>
cd url-shortener

# Run locally with Docker Compose
docker-compose up --build

# Access the app
# Frontend: http://localhost
# Backend API: http://localhost:8000/docs
# Health: http://localhost:8000/api/health
```

## Architecture

```
User → NGINX (Frontend :80) → FastAPI (Backend :8000) → PostgreSQL + Redis
                                        ↓
                                   Prometheus → Grafana
```

## Project Status

- [x] Phase 1: Application (FastAPI + React + PostgreSQL + Redis)
- [x] Phase 2: Docker (Multi-stage builds, Docker Compose)
- [ ] Phase 3: Kubernetes manifests
- [ ] Phase 4: Helm chart
- [ ] Phase 5: Monitoring (Prometheus + Grafana)
- [ ] Phase 6: CI/CD (GitHub Actions)
- [ ] Phase 7: AWS deployment
